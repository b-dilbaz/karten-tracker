-- Einmal im Supabase SQL Editor ausführen (Supabase > SQL Editor > New query > einfügen > Run).
-- Legt die Tabelle für Karten, Käufe und Wochenpreise an. Jeder sieht nur seine eigenen Einträge.

create table if not exists public.items (
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  id text not null,
  kind text not null check (kind in ('card', 'buy', 'snap')),
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  primary key (user_id, id)
);

alter table public.items enable row level security;

drop policy if exists "eigene Einträge lesen" on public.items;
drop policy if exists "eigene Einträge anlegen" on public.items;
drop policy if exists "eigene Einträge ändern" on public.items;
drop policy if exists "eigene Einträge löschen" on public.items;

create policy "eigene Einträge lesen" on public.items for select using (auth.uid() = user_id);
create policy "eigene Einträge anlegen" on public.items for insert with check (auth.uid() = user_id);
create policy "eigene Einträge ändern" on public.items for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "eigene Einträge löschen" on public.items for delete using (auth.uid() = user_id);
