<script lang="ts">
    import { onMount } from "svelte";
    import { Play, Pause, RotateCcw, Volume2 } from "lucide-svelte";
    import { Button } from "$lib/components/ui/button/index.js";
    import { Progress } from "$lib/components/ui/progress/index.js";

    let { audioSrc, taskId, text } = $props();

    let audio: HTMLAudioElement;
    let isPlaying = $state(false);
    let currentTime = $state(0);
    let duration = $state(0);
    let timestamps = $state<{word: string, start: number, end: number}[]>([]);
    let activeWordIndex = $state(-1);

    onMount(async () => {
        const res = await fetch(`/api/generations/0/timestamps?task_id=${taskId}`);
        if (res.ok) {
            timestamps = await res.json();
        }
    });

    function togglePlay() {
        if (isPlaying) audio.pause();
        else audio.play();
        isPlaying = !isPlaying;
    }

    function handleTimeUpdate() {
        currentTime = audio.currentTime;
        activeWordIndex = timestamps.findIndex(t => currentTime >= t.start && currentTime <= t.end);
        
        // Auto-scroll logic could go here
    }

    function seek(time: number) {
        audio.currentTime = time;
    }
</script>

<div class="space-y-4 p-4 bg-muted/30 rounded-xl border border-border/50">
    <audio 
        bind:this={audio} 
        src={audioSrc} 
        ontimeupdate={handleTimeUpdate}
        onloadedmetadata={() => duration = audio.duration}
        onended={() => isPlaying = false}
        class="hidden"
    ></audio>

    <!-- Karaoke Text Display -->
    <div class="flex flex-wrap gap-x-1.5 gap-y-1 p-4 min-h-[100px] text-lg leading-relaxed bg-background/50 rounded-lg border border-border/30 overflow-y-auto max-h-[200px]">
        {#if timestamps.length > 0}
            {#each timestamps as ts, i}
                <span 
                    class="transition-colors duration-200 cursor-pointer rounded px-0.5
                    {activeWordIndex === i ? 'bg-primary text-primary-foreground font-bold shadow-sm' : 'hover:bg-muted'}"
                    onclick={() => seek(ts.start)}
                >
                    {ts.word}
                </span>
            {/each}
        {:else}
            <span class="text-muted-foreground opacity-50 italic">Loading text alignment...</span>
        {/if}
    </div>

    <!-- Controls -->
    <div class="flex items-center gap-4">
        <Button variant="ghost" size="icon" onclick={togglePlay} class="h-10 w-10 shrink-0">
            {#if isPlaying}
                <Pause class="w-5 h-5 fill-current" />
            {:else}
                <Play class="w-5 h-5 fill-current" />
            {/if}
        </Button>

        <div class="flex-1 space-y-1">
            <Progress value={(currentTime / duration) * 100 || 0} max={100} class="h-1.5" />
            <div class="flex justify-between text-[10px] text-muted-foreground font-mono">
                <span>{currentTime.toFixed(1)}s</span>
                <span>{duration.toFixed(1)}s</span>
            </div>
        </div>

        <Button variant="ghost" size="icon" onclick={() => seek(0)} class="h-8 w-8">
            <RotateCcw class="w-4 h-4" />
        </Button>
    </div>
</div>
