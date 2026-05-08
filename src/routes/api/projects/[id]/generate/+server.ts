import { json } from '@sveltejs/kit';
import { queries } from '$lib/server/schema';
import { writeFileSync } from 'fs';
import path from 'path';

export async function POST({ params, request }) {
    try {
        const projectId = parseInt(params.id);
        const { text } = await request.json();
        
        if (!text) return json({ error: "Text is required" }, { status: 400 });

        queries.updateProjectContent.run(text, projectId);

        // Start FastAPI task
        const response = await fetch("http://localhost:8000/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
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

        const statusRes = await fetch(`http://localhost:8000/status/${taskId}`);
        if (!statusRes.ok) throw new Error("Task not found");
        
        const statusData = await statusRes.json();
        
        if (statusData.status === 'completed') {
            // Download audio
            const audioRes = await fetch(`http://localhost:8000/audio/${taskId}`);
            const arrayBuffer = await audioRes.arrayBuffer();
            const buffer = Buffer.from(arrayBuffer);
            
            const fileName = `tts_${projectId}_${Date.now()}.wav`;
            const filePath = path.join(process.cwd(), 'static', 'audio', fileName);
            writeFileSync(filePath, buffer);
            
            const audioPath = `/audio/${fileName}`;
            const result = queries.insertGeneration.get(projectId, text || "Generated Audio", audioPath, 0, 'AfidnaTTS') as { id: number };

            return json({
                status: 'completed',
                generation: {
                    id: result.id,
                    project_id: projectId,
                    text_snippet: text,
                    audio_path: audioPath,
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
