import { queries, type Generation } from '$lib/server/schema';
import { existsSync } from 'fs';
import { execSync } from 'child_process';
import path from 'path';

export async function GET({ params, url }) {
    try {
        const id = parseInt(params.id);
        const format = url.searchParams.get('format') || 'mp3';
        
        if (!['mp3', 'webm'].includes(format)) {
            return new Response(JSON.stringify({ error: "Unsupported format. Use mp3 or webm." }), { status: 400 });
        }

        const gen = queries.getGenerationById.get(id) as Generation | undefined;
        if (!gen) return new Response(JSON.stringify({ error: "Generation not found" }), { status: 404 });
        
        const srcPath = path.join(process.cwd(), 'static', gen.audio_path);
        if (!existsSync(srcPath)) {
            return new Response(JSON.stringify({ error: "Source audio file not found" }), { status: 404 });
        }
        
        const outName = gen.audio_path.replace('.wav', `.${format}`);
        const outPath = path.join(process.cwd(), 'static', outName);
        
        // Convert using ffmpeg
        if (!existsSync(outPath)) {
            execSync(`ffmpeg -i "${srcPath}" -y "${outPath}"`, { timeout: 30000 });
        }
        
        const mimeTypes: Record<string, string> = {
            mp3: 'audio/mpeg',
            webm: 'audio/webm'
        };
        
        const file = Bun.file(outPath);
        return new Response(file, {
            headers: {
                'Content-Type': mimeTypes[format],
                'Content-Disposition': `attachment; filename="generation_${id}.${format}"`
            }
        });
    } catch (error: any) {
        return new Response(JSON.stringify({ error: error.message || "Conversion failed" }), { status: 500 });
    }
}
