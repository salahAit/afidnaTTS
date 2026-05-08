import db from "./db";

export interface Project {
    id: number;
    title: string;
    description: string;
    content: string;
    created_at: string;
    updated_at: string;
}

export interface Generation {
    id: number;
    project_id: number;
    text_snippet: string;
    audio_path: string;
    duration: number;
    model: string;
    created_at: string;
}

export function initDb() {
    db.run(`
        CREATE TABLE IF NOT EXISTS projects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT,
            content     TEXT DEFAULT '',
            created_at  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        );
    `);

    db.run(`
        CREATE TABLE IF NOT EXISTS generations (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id    INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            text_snippet  TEXT NOT NULL,
            audio_path    TEXT NOT NULL,
            duration      REAL DEFAULT 0,
            model         TEXT DEFAULT 'F5-TTS',
            created_at    TEXT DEFAULT (datetime('now'))
        );
    `);
    
    db.run(`CREATE INDEX IF NOT EXISTS idx_generations_project ON generations(project_id);`);
}

// Automatically initialize db
initDb();

export const queries = {
    // Projects
    getProjects: db.prepare("SELECT * FROM projects ORDER BY updated_at DESC"),
    getProjectById: db.prepare("SELECT * FROM projects WHERE id = ?"),
    insertProject: db.prepare("INSERT INTO projects (title, description, content) VALUES (?, ?, ?) RETURNING id"),
    updateProject: db.prepare("UPDATE projects SET title = ?, description = ?, content = ?, updated_at = datetime('now') WHERE id = ?"),
    updateProjectContent: db.prepare("UPDATE projects SET content = ?, updated_at = datetime('now') WHERE id = ?"),
    deleteProject: db.prepare("DELETE FROM projects WHERE id = ?"),
    
    // Generations
    getGenerationsByProjectId: db.prepare("SELECT * FROM generations WHERE project_id = ? ORDER BY created_at DESC"),
    getGenerationById: db.prepare("SELECT * FROM generations WHERE id = ?"),
    insertGeneration: db.prepare(`
        INSERT INTO generations (project_id, text_snippet, audio_path, duration, model) 
        VALUES (?, ?, ?, ?, ?) RETURNING id
    `),
    deleteGeneration: db.prepare("DELETE FROM generations WHERE id = ?")
};
