// 定義活動資料介面 (用於後台管理)
export interface Event {
  id: number
  activity_name: string
  description: string
  start_date: string
  end_date: string
  location: string
  address: string
  organizer: string
  image_url: string
}

// 定義前台使用的活動資料介面
export interface Activity {
  id: number
  uid: string
  activity_name: string
  description: string
  location: string
  start_date: string
  end_date: string
  ticket_price: string
  image_url: string | string[]
  sortTime?: number
  address?: string
  organizer?: string
  source_url?: string
  latitude?: number
  longitude?: number
  created_at?: string
  updated_at?: string
}

// 定義 API 回應介面
export interface ApiResponse {
  status: string
  data: Event[]
  total: number
  message?: string
}

// 定義活動狀態類型
export type EventStatus =
  | '只限今日'
  | '即將結束'
  | '進行中'
  | '即將開始'
  | '未開始'
  | '已結束'
  | '未知';

// 定義狀態樣式映射
export const STATUS_CLASSES: Record<EventStatus, string> = {
  即將開始: 'bg-blue-100 text-blue-800',
  進行中: 'bg-green-100 text-green-800',
  已結束: 'bg-gray-100 text-gray-800',
  只限今日: 'bg-red-100 text-red-800',
  即將結束: 'bg-yellow-100 text-yellow-800',
  未開始: 'bg-purple-100 text-purple-800',
  未知: 'bg-gray-100 text-gray-800',
} as const;

// 定義狀態映射
export const STATUS_MAP = {
  ongoing: '進行中',
  upcoming: '即將開始',
  ended: '已結束',
  today: '只限今日',
  ending: '即將結束',
  not_started: '未開始',
  unknown: '未知',
} as const;

// 定義過濾選項
export const STATUS_OPTIONS = [
  { label: '全部活動', value: '' },
  { label: '只限今日', value: '只限今日' },
  { label: '即將結束', value: '即將結束' },
  { label: '進行中', value: '進行中' },
  { label: '即將開始', value: '即將開始' },
  { label: '未開始', value: '未開始' },
  { label: '已結束', value: '已結束' },
  { label: '未知', value: '未知' },
] as const;
