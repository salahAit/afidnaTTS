import { json } from '@sveltejs/kit';
import { writeFileSync, readdirSync, existsSync, unlinkSync, readFileSync } from 'fs';
import path from 'path';

const VOICES_DIR = path.join(process.cwd(), 'static', 'voices');
const VOICES_META = path.join(VOICES_DIR, 'voices.json');

function loadVoicesMeta(): any[] {
    if (existsSync(VOICES_META)) {
        return JSON.parse(readFileSync(VOICES_META, 'utf-8'));
    }
    return [];
}

function saveVoicesMeta(voices: any[]) {
    writeFileSync(VOICES_META, JSON.stringify(voices, null, 2));
}

// GET: List all custom voices
export function GET() {
    const voices = loadVoicesMeta();
    return json(voices);
}

// POST: Upload a new custom voice
export async function POST({ request }) {
    try {
        const formData = await request.formData();
        const name = formData.get('name') as string;
        const lang = formData.get('lang') as string;
        const refText = formData.get('ref_text') as string;
        const audioFile = formData.get('audio') as File;

        if (!name || !audioFile) {
            return json({ error: "Name and audio file are required" }, { status: 400 });
        }

        const id = `custom_${Date.now()}`;
        const ext = audioFile.name.split('.').pop() || 'wav';
        const fileName = `${id}.${ext}`;
        const filePath = path.join(VOICES_DIR, fileName);

        const buffer = Buffer.from(await audioFile.arrayBuffer());
        writeFileSync(filePath, buffer);

        const voice = {
            id,
            name,
            lang: lang || 'ar',
            ref_audio: filePath,
            ref_text: refText || '',
            custom: true
        };

        const voices = loadVoicesMeta();
        voices.push(voice);
        saveVoicesMeta(voices);

        return json(voice);
    } catch (error: any) {
        return json({ error: error.message || "Upload failed" }, { status: 500 });
    }
}

// DELETE: Remove a custom voice
export async function DELETE({ request }) {
    try {
        const { id } = await request.json();
        let voices = loadVoicesMeta();
        const voice = voices.find((v: any) => v.id === id);

        if (voice) {
            const audioPath = voice.ref_audio;
            if (existsSync(audioPath)) unlinkSync(audioPath);
            voices = voices.filter((v: any) => v.id !== id);
            saveVoicesMeta(voices);
        }

        return json({ success: true });
    } catch (error: any) {
        return json({ error: error.message }, { status: 500 });
    }
}
