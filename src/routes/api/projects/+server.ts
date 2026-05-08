import { json } from '@sveltejs/kit';
import { queries } from '$lib/server/schema';

export function GET() {
    try {
        const projects = queries.getProjects.all();
        return json(projects);
    } catch (error) {
        return json({ error: "Failed to fetch projects" }, { status: 500 });
    }
}

export async function POST({ request }) {
    try {
        const { title, description, content } = await request.json();
        const result = queries.insertProject.get(title || 'New Project', description || '', content || '') as { id: number };
        return json({ id: result.id, title, description, content }, { status: 201 });
    } catch (error) {
        return json({ error: "Failed to create project" }, { status: 500 });
    }
}
