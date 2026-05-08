import { json } from '@sveltejs/kit';
import { queries } from '$lib/server/schema';
import { writeFileSync, existsSync, readFileSync, mkdirSync } from 'fs';
import path from 'path';
import { BUILTIN_VOICES, type Voice } from '$lib/constants/voices';

function getAllVoices(): Voice[] {
    const dbVoices = queries.getVoices.all() as any[];
    const custom = dbVoices.map(v => ({
        id: v.id.toString(),
        name: v.name,
        lang: v.language,
        ref_audio: v.ref_audio_path,
        ref_text: v.ref_text,
        custom: true
    }));
    return [...BUILTIN_VOICES, ...custom];
}

export async function POST({ params, request }) {
    try {
        const projectId = parseInt(params.id);
        const { text, voice_id } = await request.json();
        
        if (!text) return json({ error: "Text is required" }, { status: 400 });

        const allVoices = getAllVoices();
        const selectedVoice = allVoices.find(v => v.id === voice_id) || allVoices[0];

        queries.updateProjectContent.run(text, projectId);

        // Start FastAPI task (V2 Backend)
        const response = await fetch("http://localhost:8000/api/v1/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                text,
                lang: selectedVoice.lang,
                voice_id: selectedVoice.id,
                ref_audio: selectedVoice.ref_audio,
                ref_text: selectedVoice.ref_text
            })
        });

        if (!response.ok) throw new Error("TTS Engine generation failed to start");

        const data = await response.json();
        return json({ success: true, task_id: data.task_id });

    } catch (error: any) {
        return json({ error: error.message || "Generation failed" }, { status: 500 });
    }
}

export async function GET({ url, params }) {
    try {
        const projectId = parseInt(params.id);
        const taskId = url.searchParams.get('task_id');
        const text = url.searchParams.get('text'); // Passed to save in DB later
        
        if (!taskId) return json({ error: "task_id required" }, { status: 400 });

        const statusRes = await fetch(`http://localhost:8000/api/v1/status/${taskId}`);
        if (!statusRes.ok) throw new Error("Task not found");
        
        const statusData = await statusRes.json();
        
        if (statusData.status === 'completed') {
            // Download audio
            const audioRes = await fetch(`http://localhost:8000/audio/${statusData.output_path.split('/').pop()}`);
            const arrayBuffer = await audioRes.arrayBuffer();
            const buffer = Buffer.from(arrayBuffer);
            
            const fileName = `tts_${projectId}_${Date.now()}.wav`;
            const audioDir = path.join(process.cwd(), 'static', 'audio');
            if (!existsSync(audioDir)) mkdirSync(audioDir, { recursive: true });
            
            const filePath = path.join(audioDir, fileName);
            writeFileSync(filePath, buffer);
            
            const audioPath = `/audio/${fileName}`;

            // Download Timestamps (New Phase 5 & 11)
            let timestampsUrl = "";
            try {
                const tsRes = await fetch(`http://localhost:8000/api/v1/status/${taskId}/timestamps`);
                if (tsRes.ok) {
                    const tsData = await tsRes.json();
                    const tsFileName = `ts_${projectId}_${Date.now()}.json`;
                    const tsDir = path.join(process.cwd(), 'static', 'timestamps');
                    if (!existsSync(tsDir)) mkdirSync(tsDir, { recursive: true });
                    
                    const tsFilePath = path.join(tsDir, tsFileName);
                    writeFileSync(tsFilePath, JSON.stringify(tsData));
                    timestampsUrl = `/timestamps/${tsFileName}`;
                }
            } catch (e) {
                console.error("Failed to fetch timestamps:", e);
            }

            const result = queries.insertGeneration.get(
                projectId, 
                text || "Generated Audio", 
                audioPath, 
                timestampsUrl,
                JSON.stringify({ voice_id: statusData.metadata?.voice_id }),
                0, 
                'AfidnaTTS'
            ) as { id: number };

            return json({
                status: 'completed',
                generation: {
                    id: result.id,
                    project_id: projectId,
                    text_snippet: text,
                    audio_path: audioPath,
                    timestamps_url: timestampsUrl,
                    metadata: JSON.stringify({ voice_id: statusData.metadata?.voice_id }),
                    duration: 0,
                    model: 'AfidnaTTS',
                    created_at: new Date().toISOString()
                }
            });
        }
        
        return json({ status: statusData.status, progress: statusData.progress });

    } catch (error: any) {
        return json({ error: error.message || "Status check failed" }, { status: 500 });
    }
}
