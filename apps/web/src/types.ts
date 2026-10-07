export interface Resource {
  id: string;
  provider: string;
  name: string;
  kind: string;
  color: string;
  initials: string;
  followers: number | null;
  followers_label?: string;
  content_count: number;
  mode: "daily" | "snapshot";
  source: string;
  last_sync?: string;
  connection_id?: string;
  sync_error?: string;
  live?: boolean;
  live_title?: string;
  capabilities: string[];
  coverage?: { start: string; end: string | null; requested_end: string };
}
export interface Daily {
  resource_id: string;
  day: string;
  views: number | null;
  minutes: number | null;
  gained: number | null;
  lost: number | null;
  likes: number | null;
  comments: number | null;
  shares: number | null;
  revenue: number | null;
  average_duration?: number | null;
  average_percentage?: number | null;
  source: string;
  kind: string;
}
export interface Snapshot {
  resource_id: string;
  observed_at: string;
  followers?: number | null;
  members?: number | null;
  online?: number | null;
  live_viewers?: number | null;
  live?: boolean;
  source: string;
  kind: string;
}
export interface Content {
  id: string;
  resource_id: string;
  title: string;
  published: string;
  views: number | null;
  likes: number | null;
  comments: number | null;
  shares?: number | null;
  duration?: string;
  format: string;
  scope: string;
  url?: string;
  source: string;
}
export interface Provider {
  id: string;
  name: string;
  color: string;
  status: string;
  description: string;
  fields: string[];
  capabilities: string[];
  docs: string;
  limitations: string;
}
export interface Connection {
  id: string;
  provider: string;
  label: string;
  status: string;
  last_sync?: string;
  error?: string;
}
export interface Dataset {
  demo: boolean;
  resources: Resource[];
  daily: Daily[];
  snapshots: Snapshot[];
  contents: Content[];
  breakdowns: {
    resource_id: string;
    kind: string;
    rows: { label: string; value: number; start: string; end: string }[];
  }[];
  notes: { id: string; resource_id: string; body: string; created: string }[];
  connections: Connection[];
  jobs: { id: string; connection_id: string; status: string; error?: string }[];
}
export interface Status {
  testing?: boolean;
  setup_required: boolean;
  user: { id: string; email: string; name: string } | null;
  workspaces: { id: string; name: string; role: string }[];
  catalog: Provider[];
  public_url: string;
  version: string;
}
