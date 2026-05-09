<script lang="ts">
	import { onMount } from 'svelte';

	interface WordTimestamp {
		word: string;
		start: number;
		end: number;
	}

	export let audioUrl: string;
	export let timestamps: WordTimestamp[] = [];
	export let language: string = 'ar';

	let audioPlayer: HTMLAudioElement;
	let currentTime = 0;
	let duration = 0;
	let isPlaying = false;
	let activeWordIndex = -1;

	$: {
		if (timestamps.length > 0) {
			activeWordIndex = timestamps.findIndex(
				(w) => currentTime >= w.start && currentTime <= w.end
			);
		}
	}

	function togglePlay() {
		if (isPlaying) {
			audioPlayer.pause();
		} else {
			audioPlayer.play();
		}
		isPlaying = !isPlaying;
	}

	function handleTimeUpdate() {
		currentTime = audioPlayer.currentTime;
	}

	function handleLoadedMetadata() {
		duration = audioPlayer.duration;
	}

	function seek(time: number) {
		audioPlayer.currentTime = time;
		currentTime = time;
	}
</script>

<div class="glass-card flex flex-col gap-6" dir={language === 'ar' ? 'rtl' : 'ltr'}>
	<!-- Transcript Area with Highlighting -->
	<div class="max-h-64 overflow-y-auto p-4 leading-loose text-xl text-center">
		{#if timestamps.length > 0}
			{#each timestamps as word, i}
				<span
					class="word-badge transition-all duration-200 cursor-pointer rounded px-1
                    {activeWordIndex === i
						? 'bg-primary text-primary-foreground scale-110 shadow-lg'
						: 'hover:bg-muted'}"
					on:click={() => seek(word.start)}
					on:keydown={(e) => e.key === 'Enter' && seek(word.start)}
					role="button"
					tabindex="0"
				>
					{word.word}
				</span>
			{/each}
		{:else}
			<p class="text-muted-foreground italic">No transcript available</p>
		{/if}
	</div>

	<!-- Controls -->
	<div class="flex flex-col gap-2">
		<audio
			bind:this={audioPlayer}
			src={audioUrl}
			on:timeupdate={handleTimeUpdate}
			on:loadedmetadata={handleLoadedMetadata}
			on:ended={() => (isPlaying = false)}
		></audio>

		<!-- Progress Bar -->
		<div class="relative w-full h-2 bg-muted rounded-full overflow-hidden group cursor-pointer">
			<div
				class="absolute top-0 left-0 h-full bg-primary transition-all duration-100"
				style="width: {(currentTime / duration) * 100}%"
			></div>
			<input
				type="range"
				min="0"
				max={duration}
				step="0.01"
				bind:value={currentTime}
				on:input={(e) => seek(parseFloat(e.currentTarget.value))}
				class="absolute top-0 left-0 w-full h-full opacity-0 cursor-pointer"
			/>
		</div>

		<div class="flex items-center justify-between text-sm text-muted-foreground font-mono">
			<span>{currentTime.toFixed(1)}s</span>
			<button
				on:click={togglePlay}
				class="p-3 bg-primary text-primary-foreground rounded-full hover:scale-110 transition-transform shadow-lg"
			>
				{#if isPlaying}
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					><rect x="6" y="4" width="4" height="16" /><rect x="14" y="4" width="4" height="16" /></svg>
				{:else}
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					><polygon points="5 3 19 12 5 21 5 3" /></svg>
				{/if}
			</button>
			<span>{duration.toFixed(1)}s</span>
		</div>
	</div>
</div>

<style>
	.word-badge {
		display: inline-block;
		margin: 0.2rem;
	}
</style>
