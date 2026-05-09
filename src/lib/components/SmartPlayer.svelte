<script lang="ts">
    import { onMount } from "svelte";
    import { Play, Pause, RotateCcw, Volume2 } from "lucide-svelte";
    import { Button } from "$lib/components/ui/button/index.js";
    import { Progress } from "$lib/components/ui/progress/index.js";

    let { audioSrc, taskId, text, timestampsUrl = "" } = $props();

    let audio: HTMLAudioElement;
    let isPlaying = $state(false);
    let currentTime = $state(0);
    let duration = $state(0);
    let timestamps = $state<{word: string, start: number, end: number}[]>([]);
    let activeWordIndex = $state(-1);

    onMount(async () => {
        const url = timestampsUrl || `/api/generations/0/timestamps?task_id=${taskId}`;
        const res = await fetch(url);
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

<div class="glass-card flex flex-col gap-6 p-6 transition-all duration-500 hover:shadow-2xl" dir="rtl">
    <audio 
        bind:this={audio} 
        src={audioSrc} 
        ontimeupdate={handleTimeUpdate}
        onloadedmetadata={() => duration = audio.duration}
        onended={() => isPlaying = false}
        class="hidden"
    ></audio>

    <!-- Karaoke Text Display -->
    <div class="relative flex flex-wrap gap-x-2 gap-y-2 p-6 min-h-[120px] text-xl lg:text-2xl leading-relaxed bg-background/20 rounded-2xl border border-primary/10 overflow-y-auto max-h-[250px] shadow-inner custom-scrollbar">
        {#if timestamps.length > 0}
            {#each timestamps as ts, i}
                <span 
                    class="transition-all duration-300 cursor-pointer rounded-lg px-2 py-0.5
                    {activeWordIndex === i 
                        ? 'bg-primary text-primary-foreground font-bold scale-110 shadow-lg ring-2 ring-primary/20 z-10' 
                        : 'hover:bg-primary/10 hover:text-primary opacity-80 hover:opacity-100'}"
                    onclick={() => seek(ts.start)}
                >
                    {ts.word}
                </span>
            {/each}
        {:else}
            <div class="w-full flex flex-col items-center justify-center gap-2 opacity-50">
                <Loader2 class="w-6 h-6 animate-spin text-primary" />
                <span class="text-sm italic">{i18n.t('tts.generating')}...</span>
            </div>
        {/if}
    </div>

    <!-- Controls Container -->
    <div class="flex flex-col gap-4">
        <!-- Progress Bar -->
        <div class="group relative w-full h-2 bg-primary/10 rounded-full cursor-pointer transition-all hover:h-3">
            <div 
                class="absolute top-0 left-0 h-full bg-gradient-to-r from-primary to-accent rounded-full shadow-[0_0_10px_rgba(var(--primary),0.5)] transition-all duration-100"
                style="width: {(currentTime / duration) * 100 || 0}%"
            ></div>
            <input 
                type="range" 
                min="0" 
                max={duration} 
                step="0.01" 
                value={currentTime} 
                oninput={(e) => seek(parseFloat(e.currentTarget.value))}
                class="absolute top-0 left-0 w-full h-full opacity-0 cursor-pointer z-20"
            />
        </div>

        <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
                <Button 
                    variant="ghost" 
                    size="icon" 
                    onclick={togglePlay} 
                    class="h-14 w-14 rounded-full bg-primary text-primary-foreground shadow-lg hover:scale-110 hover:bg-primary/90 transition-all active:scale-95"
                >
                    {#if isPlaying}
                        <Pause class="w-6 h-6 fill-current" />
                    {:else}
                        <Play class="w-6 h-6 fill-current ml-1" />
                    {/if}
                </Button>
                
                <div class="flex flex-col">
                    <span class="text-sm font-mono font-bold text-primary">
                        {Math.floor(currentTime / 60)}:{Math.floor(currentTime % 60).toString().padStart(2, '0')}
                    </span>
                    <span class="text-[10px] text-muted-foreground font-mono">
                        {Math.floor(duration / 60)}:{Math.floor(duration % 60).toString().padStart(2, '0')}
                    </span>
                </div>
            </div>

            <div class="flex items-center gap-2">
                <Button variant="ghost" size="icon" onclick={() => seek(0)} class="h-10 w-10 hover:bg-primary/10 rounded-full">
                    <RotateCcw class="w-4 h-4" />
                </Button>
                <div class="w-px h-6 bg-border mx-1"></div>
                <Button variant="ghost" size="icon" class="h-10 w-10 hover:bg-primary/10 rounded-full">
                    <Volume2 class="w-4 h-4" />
                </Button>
            </div>
        </div>
    </div>
</div>

<style>
    .custom-scrollbar::-webkit-scrollbar {
        width: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
        background: transparent;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
        @apply bg-primary/20 rounded-full;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
        @apply bg-primary/40;
    }
</style>
