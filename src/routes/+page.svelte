<script lang="ts">
	import { Plus, FolderOpen, Calendar, Trash2 } from "lucide-svelte";
	import { Button } from "$lib/components/ui/button/index.js";
	import * as Card from "$lib/components/ui/card/index.js";
	import * as Dialog from "$lib/components/ui/dialog/index.js";
	import { Input } from "$lib/components/ui/input/index.js";
	import { i18n } from "$lib/stores/i18n.svelte";
	import { toast } from "svelte-sonner";
	import { invalidateAll } from "$app/navigation";

	let { data } = $props();
	let projects = $derived(data.projects || []);

	let isCreating = $state(false);
	let newTitle = $state("");
	let newDesc = $state("");
	let dialogOpen = $state(false);

	async function createProject() {
		if (!newTitle.trim()) return;
		isCreating = true;
		try {
			const res = await fetch('/api/projects', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ title: newTitle, description: newDesc, content: '' })
			});
			if (res.ok) {
				toast.success("Project created");
				dialogOpen = false;
				newTitle = "";
				newDesc = "";
				await invalidateAll();
			} else {
				toast.error("Failed to create project");
			}
		} catch (e) {
			toast.error("Error creating project");
		} finally {
			isCreating = false;
		}
	}

	async function deleteProject(id: number) {
		if (!confirm("Are you sure?")) return;
		try {
			await fetch(`/api/projects/${id}`, { method: 'DELETE' });
			toast.success("Deleted successfully");
			await invalidateAll();
		} catch (e) {
			toast.error("Error deleting");
		}
	}
</script>

<svelte:head>
	<title>{i18n.t('app.title')} | {i18n.t('nav.projects')}</title>
</svelte:head>

<div class="flex-1 flex flex-col items-center p-6 lg:p-12">
	<div class="w-full max-w-5xl space-y-8">
		<header class="flex flex-col md:flex-row justify-between items-center gap-4">
			<div>
				<h1 class="text-3xl font-bold tracking-tight">{i18n.t('tts.hero.title')}</h1>
				<p class="text-muted-foreground mt-1">{i18n.t('tts.hero.desc')}</p>
			</div>
			
			<Dialog.Root bind:open={dialogOpen}>
				<Dialog.Trigger>
					{#snippet child({ props })}
						<Button {...props} class="gap-2 shadow-lg">
							<Plus class="w-4 h-4" />
							{i18n.t('proj.new')}
						</Button>
					{/snippet}
				</Dialog.Trigger>
				<Dialog.Content>
					<Dialog.Header>
						<Dialog.Title>{i18n.t('proj.new')}</Dialog.Title>
					</Dialog.Header>
					<div class="space-y-4 py-4" dir={i18n.dir}>
						<div class="space-y-2">
							<label class="text-sm font-medium" for="title">{i18n.t('proj.title')}</label>
							<Input id="title" bind:value={newTitle} />
						</div>
						<div class="space-y-2">
							<label class="text-sm font-medium" for="desc">{i18n.t('proj.desc')}</label>
							<Input id="desc" bind:value={newDesc} />
						</div>
					</div>
					<Dialog.Footer>
						<Button variant="outline" onclick={() => dialogOpen = false}>{i18n.t('proj.cancel')}</Button>
						<Button onclick={createProject} disabled={isCreating || !newTitle.trim()}>
							{i18n.t('proj.create')}
						</Button>
					</Dialog.Footer>
				</Dialog.Content>
			</Dialog.Root>
		</header>

		{#if projects.length === 0}
			<Card.Root class="border-dashed bg-transparent shadow-none">
				<Card.Content class="flex flex-col items-center justify-center p-12 text-center text-muted-foreground">
					<FolderOpen class="w-12 h-12 mb-4 opacity-20" />
					<p>{i18n.t('proj.no_projects')}</p>
				</Card.Content>
			</Card.Root>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each projects as project}
					<Card.Root class="group relative overflow-hidden glass-card hover:border-primary/50 transition-colors">
						<Card.Header class="pb-2">
							<Card.Title class="text-xl truncate">{project.title}</Card.Title>
							<Card.Description class="truncate">{project.description || '...'}</Card.Description>
						</Card.Header>
						<Card.Content>
							<div class="flex items-center text-xs text-muted-foreground mt-4 gap-2">
								<Calendar class="w-3 h-3" />
								{new Date(project.created_at).toLocaleDateString()}
							</div>
						</Card.Content>
						
						<!-- Hover Actions -->
						<div class="absolute inset-0 bg-background/80 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
							<Button href="/project/{project.id}" class="shadow-xl">
								<FolderOpen class="w-4 h-4 mr-2" /> Open
							</Button>
							<Button variant="destructive" size="icon" class="shadow-xl" onclick={() => deleteProject(project.id)}>
								<Trash2 class="w-4 h-4" />
							</Button>
						</div>
					</Card.Root>
				{/each}
			</div>
		{/if}
	</div>
</div>
