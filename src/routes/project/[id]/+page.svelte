<script lang="ts">
	import { Play, Download, Loader2, ArrowLeft, Clock, Save, Trash2, Calendar } from "lucide-svelte";
	import { Textarea } from "$lib/components/ui/textarea/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import * as Card from "$lib/components/ui/card/index.js";
	import { Progress } from "$lib/components/ui/progress/index.js";
	import { i18n } from "$lib/stores/i18n.svelte";
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
				body: JSON.stringify({ text })
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
        if (!confirm("Are you sure you want to delete this audio?")) return;
        toast.info("Deletion will be implemented.");
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

                    <div class="flex justify-end pt-4 border-t border-border/50">
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
                                        <Button variant="ghost" size="icon" class="h-6 w-6" href={gen.audio_path} download="audio_{gen.id}.wav">
                                            <Download class="w-3 h-3" />
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
