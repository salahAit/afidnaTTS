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
    timestamps_url: string;
    metadata: string;
    duration: number;
    model: string;
    created_at: string;
}

export interface Voice {
    id: number;
    name: string;
    ref_audio_path: string;
    ref_text: string;
    gender: string;
    language: string;
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
            timestamps_url TEXT,
            metadata      TEXT,
            duration      REAL DEFAULT 0,
            model         TEXT DEFAULT 'F5-TTS',
            created_at    TEXT DEFAULT (datetime('now'))
        );
    `);

    db.run(`
        CREATE TABLE IF NOT EXISTS voices (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            ref_audio_path  TEXT NOT NULL,
            ref_text        TEXT,
            gender          TEXT,
            language        TEXT DEFAULT 'ar',
            created_at      TEXT DEFAULT (datetime('now'))
        );
    `);
    
    db.run(`CREATE INDEX IF NOT EXISTS idx_generations_project ON generations(project_id);`);

    // Migration: Add missing columns if they don't exist
    try {
        db.run("ALTER TABLE generations ADD COLUMN timestamps_url TEXT;");
    } catch (e) {
        // Column probably already exists
    }
    try {
        db.run("ALTER TABLE generations ADD COLUMN metadata TEXT;");
    } catch (e) {
        // Column probably already exists
    }
}

// Initialize database immediately to ensure schema is ready for preparations
initDb();

export const queries = {
    getProjects: db.prepare("SELECT * FROM projects ORDER BY created_at DESC"),
    getProject: db.prepare("SELECT * FROM projects WHERE id = ?"),
    insertProject: db.prepare("INSERT INTO projects (title, description, content) VALUES (?, ?, ?) RETURNING id"),
    updateProjectContent: db.prepare("UPDATE projects SET content = ? WHERE id = ?"),
    deleteProject: db.prepare("DELETE FROM projects WHERE id = ?"),
    
    getGenerations: db.prepare("SELECT * FROM generations WHERE project_id = ? ORDER BY created_at DESC"),
    insertGeneration: db.prepare(`
        INSERT INTO generations (project_id, text_snippet, audio_path, timestamps_url, metadata, duration, model) 
        VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id
    `),
    deleteGeneration: db.prepare("DELETE FROM generations WHERE id = ?"),
    
    getVoices: db.prepare("SELECT * FROM voices ORDER BY name ASC"),
    insertVoice: db.prepare("INSERT INTO voices (name, ref_audio_path, ref_text, gender, language) VALUES (?, ?, ?, ?, ?) RETURNING id"),
    deleteVoice: db.prepare("DELETE FROM voices WHERE id = ?")
};
