import { json } from '@sveltejs/kit';
import { queries, type Generation } from '$lib/server/schema';
import { unlinkSync, existsSync } from 'fs';
import path from 'path';

export function DELETE({ params }) {
    try {
        const id = parseInt(params.id);
        const gen = queries.getGenerationById.get(id) as Generation | undefined;
        
        if (!gen) return json({ error: "Generation not found" }, { status: 404 });
        
        // Delete audio file from disk
        const filePath = path.join(process.cwd(), 'static', gen.audio_path);
        if (existsSync(filePath)) {
            unlinkSync(filePath);
        }
        
        // Delete from DB
        queries.deleteGeneration.run(id);
        
        return json({ success: true });
    } catch (error: any) {
        return json({ error: error.message || "Failed to delete generation" }, { status: 500 });
    }
}
