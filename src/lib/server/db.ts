import { Database } from "bun:sqlite";

// Create db and export
const db = new Database("data/tts.db", { create: true });

// Performance optimizations for concurrent operations
db.run("PRAGMA journal_mode = WAL;");
db.run("PRAGMA synchronous = NORMAL;");
db.run("PRAGMA foreign_keys = ON;");

export default db;
