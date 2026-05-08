import { json } from '@sveltejs/kit';
import { queries } from '$lib/server/schema';

export function GET({ params }) {
    try {
        const id = parseInt(params.id);
        const project = queries.getProjectById.get(id);
        
        if (!project) {
            return json({ error: "Project not found" }, { status: 404 });
        }
        
        const generations = queries.getGenerationsByProjectId.all(id);
        return json({ project, generations });
    } catch (error) {
        return json({ error: "Failed to fetch project details" }, { status: 500 });
    }
}

export async function PUT({ params, request }) {
    try {
        const id = parseInt(params.id);
        const { title, description, content } = await request.json();
        
        if (content !== undefined && title === undefined) {
             queries.updateProjectContent.run(content, id);
        } else {
             queries.updateProject.run(title, description, content, id);
        }
        
        return json({ success: true });
    } catch (error) {
        return json({ error: "Failed to update project" }, { status: 500 });
    }
}

export function DELETE({ params }) {
    try {
        const id = parseInt(params.id);
        queries.deleteProject.run(id);
        return json({ success: true });
    } catch (error) {
        return json({ error: "Failed to delete project" }, { status: 500 });
    }
}
