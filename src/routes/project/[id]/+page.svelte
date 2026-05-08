<script lang="ts">
	import { Play, Download, Loader2, ArrowLeft, Clock, Save, Trash2, Calendar, FileAudio, Plus, Mic } from "lucide-svelte";
	import * as DropdownMenu from "$lib/components/ui/dropdown-menu/index.js";
	import * as Dialog from "$lib/components/ui/dialog/index.js";
	import { Textarea } from "$lib/components/ui/textarea/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { Input } from "$lib/components/ui/input/index.js";
	import * as Card from "$lib/components/ui/card/index.js";
	import { Progress } from "$lib/components/ui/progress/index.js";
    import * as Select from "$lib/components/ui/select/index.js";
	import { i18n } from "$lib/stores/i18n.svelte";
	import { BUILTIN_VOICES, type Voice } from "$lib/constants/voices";
	import { toast } from "svelte-sonner";
	import { invalidateAll } from "$app/navigation";
    import { onMount } from "svelte";

	let { data } = $props();
	
	let project = $derived(data.project);
	let generations = $derived(data.generations || []);

	let text = $state(project?.content || "");
	let loading = $state(false);
	let isSaving = $state(false);
    
    let progressValue = $state(0);
    let progressText = $state("");
    let selectedVoiceId = $state(BUILTIN_VOICES[0].id);
    let customVoices = $state<Voice[]>([]);
    let allVoices = $derived([...BUILTIN_VOICES, ...customVoices]);

    const selectedVoiceLabel = $derived(
        allVoices.find((v) => v.id === selectedVoiceId)?.name ?? i18n.t('tts.voice_select')
    );

    // Voice upload dialog state
    let voiceDialogOpen = $state(false);
    let newVoiceName = $state('');
    let newVoiceLang = $state('ar');
    let newVoiceRefText = $state('');
    let newVoiceFile: File | null = $state(null);

    onMount(async () => {
        const res = await fetch('/api/voices');
        if (res.ok) customVoices = await res.json();
    });

    async function uploadVoice() {
        if (!newVoiceName || !newVoiceFile) return;
        const formData = new FormData();
        formData.append('name', newVoiceName);
        formData.append('lang', newVoiceLang);
        formData.append('ref_text', newVoiceRefText);
        formData.append('audio', newVoiceFile);
        try {
            const res = await fetch('/api/voices', { method: 'POST', body: formData });
            if (res.ok) {
                const voice = await res.json();
                customVoices = [...customVoices, voice];
                selectedVoiceId = voice.id;
                voiceDialogOpen = false;
                newVoiceName = ''; newVoiceRefText = ''; newVoiceFile = null;
                toast.success('Voice added!');
            }
        } catch (e) { toast.error('Upload failed'); }
    }

    $effect(() => {
        if (project) {
            text = project.content || "";
        }
    });

    async function saveContent(silent = false) {
        if (isSaving || text === project.content) return;
        isSaving = true;
        try {
            await fetch(`/api/projects/${project.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: text })
            });
            if (!silent) toast.success("Saved");
        } catch (e) {
            if (!silent) toast.error("Error saving");
        } finally {
            isSaving = false;
        }
    }

	async function generateSpeech() {
		if (!text.trim()) return;
		loading = true;
        progressValue = 0;
        progressText = "Starting...";

		try {
            // Start generation
			const res = await fetch(`/api/projects/${project.id}/generate`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ text, voice_id: selectedVoiceId })
			});

			if (!res.ok) throw new Error(i18n.t('tts.error'));
            
            const startData = await res.json();
            const taskId = startData.task_id;
            
            // Polling loop
            while (true) {
                await new Promise(r => setTimeout(r, 1000)); // Poll every 1s
                const statusRes = await fetch(`/api/projects/${project.id}/generate?task_id=${taskId}&text=${encodeURIComponent(text)}`);
                const statusData = await statusRes.json();
                
                if (statusData.status === 'completed') {
                    toast.success("تم توليد الصوت بنجاح! / Audio generated successfully!");
                    await invalidateAll(); // Refresh history
                    break;
                } else if (statusData.status === 'failed') {
                    throw new Error(statusData.progress || i18n.t('tts.error'));
                }
                
                // Parse progress string
                progressText = statusData.progress;
                if (progressText && progressText.includes('%')) {
                    const match = progressText.match(/(\d+)%/);
                    if (match) progressValue = parseInt(match[1]);
                }
            }
		} catch (e: any) {
			toast.error(e.message || i18n.t('tts.error'));
		} finally {
			loading = false;
            progressValue = 0;
            progressText = "";
		}
	}

    async function deleteGeneration(genId: number) {
        if (!confirm("Delete this audio?")) return;
        try {
            const res = await fetch(`/api/generations/${genId}`, { method: 'DELETE' });
            if (res.ok) {
                toast.success("Deleted");
                await invalidateAll();
            } else {
                toast.error("Failed to delete");
            }
        } catch (e) {
            toast.error("Error deleting");
        }
    }

    function convertGeneration(genId: number, format: string) {
        window.open(`/api/generations/${genId}/convert?format=${format}`, '_blank');
    }
</script>

<svelte:head>
	<title>{project?.title} - {i18n.t('app.title')}</title>
</svelte:head>

<div class="flex-1 flex flex-col p-4 lg:p-8 space-y-6 max-w-7xl mx-auto w-full">
    <!-- Header -->
    <div class="flex items-center justify-between gap-4 border-b border-border/50 pb-4">
        <div class="flex items-center gap-4">
            <Button variant="ghost" size="icon" href="/">
                <ArrowLeft class="w-5 h-5 {i18n.dir === 'rtl' ? 'rotate-180' : ''}" />
            </Button>
            <div>
                <h1 class="text-2xl font-bold">{project?.title}</h1>
                <p class="text-sm text-muted-foreground">{project?.description}</p>
            </div>
        </div>
        <Button variant="outline" size="sm" onclick={() => saveContent(false)} disabled={isSaving} class="gap-2">
            <Save class="w-4 h-4" /> Save
        </Button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Editor Area -->
        <div class="lg:col-span-2 space-y-4">
            <Card.Root class="border-border/50 shadow-xl bg-background/50 backdrop-blur-xl h-full flex flex-col relative overflow-hidden">
                <Card.Content class="p-4 sm:p-6 flex-1 flex flex-col gap-4">
                    <Textarea
                        bind:value={text}
                        onblur={() => saveContent(true)}
                        placeholder={i18n.t('tts.placeholder')}
                        dir={i18n.dir}
                        class="flex-1 min-h-[300px] text-lg lg:text-xl resize-none bg-transparent focus-visible:ring-0 border-none shadow-none p-0"
                    />

                    {#if loading}
                    <div class="pt-4 border-t border-border/50 space-y-2">
                        <div class="flex justify-between text-xs text-muted-foreground" dir="ltr">
                            <span class="truncate pr-4">{progressText}</span>
                            <span>{progressValue}%</span>
                        </div>
                        <Progress value={progressValue} max={100} class="h-2" />
                    </div>
                    {/if}

                    <div class="flex flex-col sm:flex-row justify-between items-stretch sm:items-center pt-4 border-t border-border/50 gap-3">
                        <div class="flex items-center gap-2">
                            <span class="text-sm font-medium text-muted-foreground whitespace-nowrap">{i18n.t('tts.voice')}:</span>
                            <Select.Root type="single" value={selectedVoiceId} onValueChange={(v) => { if (v) selectedVoiceId = v; }}>
                                <Select.Trigger class="w-[200px]">
                                    {selectedVoiceLabel}
                                </Select.Trigger>
                                <Select.Content>
                                    {#each allVoices as voice}
                                        <Select.Item value={voice.id}>
                                            {voice.name} ({voice.lang})
                                            {#if voice.custom}
                                                <span class="text-[10px] ml-1 opacity-50">✦</span>
                                            {/if}
                                        </Select.Item>
                                    {/each}
                                </Select.Content>
                            </Select.Root>
                            <Button variant="outline" size="icon" class="h-9 w-9" onclick={() => voiceDialogOpen = true} title="Add Voice">
                                <Plus class="w-4 h-4" />
                            </Button>
                        </div>
                        <Button
                            onclick={generateSpeech}
                            disabled={loading || !text.trim()}
                            size="lg"
                            class="w-full sm:w-auto gap-2 text-primary-foreground font-bold shadow-lg transition-all"
                        >
                            {#if loading}
                                <Loader2 class="w-5 h-5 animate-spin" />
                                {i18n.t('tts.generating')}
                            {:else}
                                <Play class="w-5 h-5 fill-current" />
                                {i18n.t('tts.generate')}
                            {/if}
                        </Button>
                    </div>
                </Card.Content>
            </Card.Root>
        </div>

        <!-- Generation History Sidebar -->
        <div class="space-y-4">
            <h2 class="font-bold text-lg flex items-center gap-2">
                <Clock class="w-5 h-5 text-primary" /> 
                {i18n.t('proj.history')}
            </h2>
            
            <div class="space-y-3">
                {#if generations.length === 0}
                    <div class="p-8 text-center border border-dashed rounded-xl text-muted-foreground text-sm">
                        {i18n.t('proj.no_history')}
                    </div>
                {:else}
                    {#each generations as gen}
                        <Card.Root class="glass-card overflow-hidden">
                            <Card.Content class="p-3 space-y-3">
                                <p class="text-xs text-muted-foreground line-clamp-2" dir={i18n.dir}>
                                    "{gen.text_snippet}"
                                </p>
                                
                                <audio src={gen.audio_path} controls class="w-full h-8"></audio>
                                
                                <div class="flex justify-between items-center text-[10px] text-muted-foreground">
                                    <span class="flex items-center gap-1">
                                        <Calendar class="w-3 h-3" />
                                        {new Date(gen.created_at).toLocaleString()}
                                    </span>
                                    <div class="flex gap-1">
                                        <Button variant="ghost" size="icon" class="h-6 w-6" href={gen.audio_path} download="audio_{gen.id}.wav" title="WAV">
                                            <Download class="w-3 h-3" />
                                        </Button>
                                        <DropdownMenu.Root>
                                            <DropdownMenu.Trigger>
                                                {#snippet child({ props })}
                                                    <Button variant="ghost" size="icon" class="h-6 w-6" {...props} title="Convert">
                                                        <FileAudio class="w-3 h-3" />
                                                    </Button>
                                                {/snippet}
                                            </DropdownMenu.Trigger>
                                            <DropdownMenu.Content align="end">
                                                <DropdownMenu.Item onclick={() => convertGeneration(gen.id, 'mp3')}>MP3</DropdownMenu.Item>
                                                <DropdownMenu.Item onclick={() => convertGeneration(gen.id, 'webm')}>WebM</DropdownMenu.Item>
                                            </DropdownMenu.Content>
                                        </DropdownMenu.Root>
                                        <Button variant="ghost" size="icon" class="h-6 w-6 text-destructive hover:text-destructive" onclick={() => deleteGeneration(gen.id)} title="Delete">
                                            <Trash2 class="w-3 h-3" />
                                        </Button>
                                    </div>
                                </div>
                            </Card.Content>
                        </Card.Root>
                    {/each}
                {/if}
            </div>
        </div>
    </div>
</div>

<!-- Add Voice Dialog -->
<Dialog.Root bind:open={voiceDialogOpen}>
    <Dialog.Content>
        <Dialog.Header>
            <Dialog.Title class="flex items-center gap-2">
                <Mic class="w-5 h-5" /> Add Custom Voice
            </Dialog.Title>
            <Dialog.Description>
                Upload a short audio clip (5-15s) to use as a voice reference for generation.
            </Dialog.Description>
        </Dialog.Header>
        <div class="space-y-4 py-4">
            <div class="space-y-2">
                <label class="text-sm font-medium" for="voice-name">Voice Name</label>
                <Input id="voice-name" bind:value={newVoiceName} placeholder="e.g. Arabic Female 1" />
            </div>
            <div class="space-y-2">
                <label class="text-sm font-medium" for="voice-lang">Language</label>
                <Select.Root type="single" value={newVoiceLang} onValueChange={(v) => { if (v) newVoiceLang = v; }}>
                    <Select.Trigger class="w-full">
                        {newVoiceLang === 'ar' ? 'العربية (ar)' : newVoiceLang === 'en' ? 'English (en)' : newVoiceLang === 'fr' ? 'Français (fr)' : newVoiceLang}
                    </Select.Trigger>
                    <Select.Content>
                        <Select.Item value="ar">العربية (ar)</Select.Item>
                        <Select.Item value="en">English (en)</Select.Item>
                        <Select.Item value="fr">Français (fr)</Select.Item>
                        <Select.Item value="zh">中文 (zh)</Select.Item>
                    </Select.Content>
                </Select.Root>
            </div>
            <div class="space-y-2">
                <label class="text-sm font-medium" for="voice-ref-text">Reference Text (optional)</label>
                <Textarea id="voice-ref-text" bind:value={newVoiceRefText} placeholder="The exact text spoken in the audio clip. Leave empty for auto-transcription." rows={2} />
            </div>
            <div class="space-y-2">
                <label class="text-sm font-medium" for="voice-file">Audio File (.wav, .mp3, .flac)</label>
                <input id="voice-file" type="file" accept="audio/*" class="block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20 cursor-pointer" onchange={(e) => { const t = e.target as HTMLInputElement; newVoiceFile = t.files?.[0] ?? null; }} />
            </div>
        </div>
        <Dialog.Footer>
            <Button variant="outline" onclick={() => voiceDialogOpen = false}>Cancel</Button>
            <Button onclick={uploadVoice} disabled={!newVoiceName || !newVoiceFile}>
                Upload & Select
            </Button>
        </Dialog.Footer>
    </Dialog.Content>
</Dialog.Root>
