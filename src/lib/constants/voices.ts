export interface Voice {
	id: string;
	name: string;
	lang: string;
	ref_audio: string;
	ref_text: string;
	custom?: boolean;
}

// Built-in voices (from F5-TTS examples)
export const BUILTIN_VOICES: Voice[] = [
	{
		id: "ar_default",
		name: "العربية (Default)",
		lang: "ar",
		ref_audio: "/voices/arabic_ref.wav",
		ref_text: "لا يمر يوم إلا وأستقبل عدة رسائل تتضمن أسئلة ملحة"
	},
	{
		id: "en_default",
		name: "English Default",
		lang: "en",
		ref_audio: "/home/msi/f5-tts/venv/lib/python3.12/site-packages/f5_tts/infer/examples/basic/basic_ref_en.wav",
		ref_text: "Some call me nature, others call me mother nature."
	},
	{
		id: "zh_default",
		name: "Chinese Default",
		lang: "zh",
		ref_audio: "/home/msi/f5-tts/venv/lib/python3.12/site-packages/f5_tts/infer/examples/basic/basic_ref_zh.wav",
		ref_text: ""
	}
];
