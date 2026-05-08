export async function load({ fetch }) {
    const res = await fetch('/api/projects');
    const projects = await res.json();
    return { projects };
}
