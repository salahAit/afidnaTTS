import { json } from '@sveltejs/kit';
import { existsSync, readFileSync } from 'fs';
import path from 'path';

export async function GET({ url }) {
    const taskId = url.searchParams.get('task_id');
    if (!taskId) return json({ error: "task_id required" }, { status: 400 });

    const timestampPath = path.join(process.cwd(), 'backend', 'storage', 'timestamps', `${taskId}.json`);
    
    if (existsSync(timestampPath)) {
        const data = JSON.parse(readFileSync(timestampPath, 'utf-8'));
        return json(data);
    }
    
    return json({ error: "Timestamps not found" }, { status: 404 });
}
