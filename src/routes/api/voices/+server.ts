import { json } from '@sveltejs/kit';
import { writeFileSync, readdirSync, existsSync, unlinkSync, readFileSync } from 'fs';
import path from 'path';
import { queries } from '$lib/server/schema';

const VOICES_DIR = path.join(process.cwd(), 'static', 'voices');
const VOICES_META = path.join(VOICES_DIR, 'voices.json');

// GET: List all custom voices
export function GET() {
    const voices = queries.getVoices.all();
    // Map database fields to the format expected by the frontend
    const mappedVoices = voices.map((v: any) => ({
        id: v.id.toString(),
        name: v.name,
        lang: v.language,
        ref_audio: v.ref_audio_path,
        ref_text: v.ref_text,
        gender: v.gender,
        custom: true
    }));
    return json(mappedVoices);
}

// POST: Upload a new custom voice
export async function POST({ request }) {
    try {
        const formData = await request.formData();
        const name = formData.get('name') as string;
        const lang = formData.get('lang') as string;
        const refText = formData.get('ref_text') as string;
        const audioFile = formData.get('audio') as File;

        if (!name || !audioFile) {
            return json({ error: "Name and audio file are required" }, { status: 400 });
        }

        const ext = audioFile.name.split('.').pop() || 'wav';
        const fileName = `voice_${Date.now()}.${ext}`;
        const filePath = path.join(VOICES_DIR, fileName);
        const publicPath = `/voices/${fileName}`;

        if (!existsSync(VOICES_DIR)) {
            const { mkdirSync } = await import('fs');
            mkdirSync(VOICES_DIR, { recursive: true });
        }

        const buffer = Buffer.from(await audioFile.arrayBuffer());
        writeFileSync(filePath, buffer);

        const result = queries.insertVoice.get(
            name,
            publicPath,
            refText || '',
            'unknown', // default gender
            lang || 'ar'
        ) as { id: number };

        const voice = {
            id: result.id.toString(),
            name,
            lang: lang || 'ar',
            ref_audio: publicPath,
            ref_text: refText || '',
            custom: true
        };

        return json(voice);
    } catch (error: any) {
        return json({ error: error.message || "Upload failed" }, { status: 500 });
    }
}

// DELETE: Remove a custom voice
export async function DELETE({ request }) {
    try {
        const { id } = await request.json();
        const voiceId = parseInt(id);
        
        // Find voice to get its path for deletion
        const db = await import('$lib/server/db');
        const voice = db.default.prepare("SELECT * FROM voices WHERE id = ?").get(voiceId) as any;

        if (voice) {
            const publicPath = voice.ref_audio_path;
            const absolutePath = path.join(process.cwd(), 'static', publicPath);
            if (existsSync(absolutePath)) unlinkSync(absolutePath);
            queries.deleteVoice.run(voiceId);
        }

        return json({ success: true });
    } catch (error: any) {
        return json({ error: error.message }, { status: 500 });
    }
}

