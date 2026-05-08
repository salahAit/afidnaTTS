import { error } from '@sveltejs/kit';

export async function load({ params, fetch }) {
    const res = await fetch(`/api/projects/${params.id}`);
    
    if (!res.ok) {
        throw error(404, 'Project not found');
    }
    
    const data = await res.json();
    return data; // { project, generations }
}
