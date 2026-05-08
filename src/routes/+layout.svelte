<script lang="ts">
	import '../app.css';
	import { theme } from '$lib/stores/theme.svelte';
	import { i18n } from '$lib/stores/i18n.svelte';
	import { Sun, Moon, Home, Menu, Volume2 } from 'lucide-svelte';
	import { page } from '$app/stores';
	import * as Sheet from "$lib/components/ui/sheet/index.js";
	import * as DropdownMenu from "$lib/components/ui/dropdown-menu/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { cn } from "$lib/utils.js";
	import { Toaster } from "$lib/components/ui/sonner/index.js";
	
	let { children } = $props();

	// Initialize theme and i18n on mount
	theme.init();
	i18n.init();
</script>

<Toaster />

<div class="relative h-screen hero-gradient flex flex-col overflow-hidden selection:bg-blue-500/30" dir={i18n.dir}>
	<!-- Navbar (Shadcn-inspired Responsive) -->
	<nav class="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
		<div class="container mx-auto max-w-7xl px-4 lg:px-8">
			<div class="flex h-16 items-center justify-between">
				<!-- Brand -->
				<div class="flex items-center gap-8">
					<a href="/" class={cn("flex items-center space-x-2 group transition-all", i18n.lang === 'ar' && "space-x-reverse")}>
						<div class="p-2 bg-blue-600/20 rounded-xl border border-blue-500/30">
							<Volume2 class="w-6 h-6 text-blue-500 group-hover:scale-110 transition-transform" />
						</div>
						<div class="flex flex-col">
							<span class="text-sm font-bold leading-none tracking-tight">{i18n.t('app.title')}</span>
							<span class="text-[10px] text-muted-foreground font-medium uppercase tracking-widest mt-0.5">{i18n.t('app.subtitle')}</span>
						</div>
					</a>

					<!-- Desktop Menu -->
					<div class="hidden md:flex items-center gap-1">
						<Button 
							variant={$page.url.pathname === '/' ? 'secondary' : 'ghost'} 
							href="/" 
							class="text-xs font-bold gap-2"
						>
							<Home size={14} />
							{i18n.t('nav.projects')}
						</Button>
					</div>
				</div>

				<!-- Toolbar -->
				<div class="flex items-center gap-2">
					<!-- Language Switcher -->
					<DropdownMenu.Root>
						<DropdownMenu.Trigger>
							{#snippet child({ props })}
								<Button variant="ghost" size="icon" {...props} class="rounded-full text-lg">
									{#if i18n.lang === 'ar'}🇩🇿{:else if i18n.lang === 'fr'}🇫🇷{:else}🇺🇸{/if}
									<span class="sr-only">{i18n.t('nav.switch_lang')}</span>
								</Button>
							{/snippet}
						</DropdownMenu.Trigger>
						<DropdownMenu.Content align="end" class="w-36">
							<DropdownMenu.Item onclick={() => i18n.setLang('ar')} class={cn("font-bold cursor-pointer gap-2", i18n.lang === 'ar' && "text-primary")}>
								<span class="text-base">🇩🇿</span> العربية
							</DropdownMenu.Item>
							<DropdownMenu.Item onclick={() => i18n.setLang('en')} class={cn("font-bold cursor-pointer gap-2", i18n.lang === 'en' && "text-primary")}>
								<span class="text-base">🇺🇸</span> English
							</DropdownMenu.Item>
							<DropdownMenu.Item onclick={() => i18n.setLang('fr')} class={cn("font-bold cursor-pointer gap-2", i18n.lang === 'fr' && "text-primary")}>
								<span class="text-base">🇫🇷</span> Français
							</DropdownMenu.Item>
						</DropdownMenu.Content>
					</DropdownMenu.Root>

					<Button 
						variant="ghost" 
						size="icon" 
						onclick={() => theme.toggle()}
						class="rounded-full"
					>
						{#if theme.isDark}
							<Sun size={18} />
						{:else}
							<Moon size={18} />
						{/if}
						<span class="sr-only">{i18n.t('nav.toggle_theme')}</span>
					</Button>

					<!-- Mobile Sheet Menu -->
					<div class="md:hidden">
						<Sheet.Root>
							<Sheet.Trigger>
								{#snippet child({ props })}
									<Button variant="ghost" size="icon" {...props}>
										<Menu size={20} />
										<span class="sr-only">{i18n.t('nav.toggle_menu')}</span>
									</Button>
								{/snippet}
							</Sheet.Trigger>
							<Sheet.Content side={i18n.lang === 'ar' ? 'right' : 'left'} class="w-80">
								<Sheet.Header class="text-start">
									<Sheet.Title class="text-lg font-bold">{i18n.t('nav.browse')}</Sheet.Title>
									<Sheet.Description class="text-xs">
										{i18n.t('nav.manage')}
									</Sheet.Description>
								</Sheet.Header>
								<div class="grid gap-2 py-6">
									<Button 
										variant={$page.url.pathname === '/' ? 'secondary' : 'ghost'} 
										href="/" 
										class="justify-start gap-4 h-12 text-sm font-bold border-none"
									>
										<div class="size-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
											<Home size={18} />
										</div>
										{i18n.t('nav.projects')}
									</Button>
								</div>
							</Sheet.Content>
						</Sheet.Root>
					</div>
				</div>
			</div>
		</div>
	</nav>

	<main class="flex-1 flex flex-col min-h-0 overflow-auto">
		{@render children()}
	</main>
</div>
