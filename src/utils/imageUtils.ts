/**
 * 處理圖片URL，確保它們是可訪問的完整URL
 * @param url 原始URL字符串
 * @returns 處理後的完整URL
 */
export function formatImageUrl(url: string | undefined): string {
  if (!url || url.trim() === '') {
    return '/images/no-image.png';
  }
  
  // 如果已經是完整URL，直接返回
  if (url.startsWith('http')) {
    return url;
  }
  
  // 如果是相對路徑，補全基礎URL
  const baseUrl = window.location.origin;
  const cleanUrl = url.startsWith('/') ? url : `/${url}`;
  return `${baseUrl}${cleanUrl}`;
}

/**
 * 為資料庫中的圖片URL生成代理URL
 * @param url 原始URL字符串
 * @param apiBaseUrl API基礎URL
 * @returns 處理後的代理URL或完整URL
 */
export function getProxiedImageUrl(url: string | undefined, apiBaseUrl: string = 'http://localhost:8000'): string {
  if (!url || url.trim() === '') {
    return '/images/no-image.png';
  }
  
  // 如果已經是代理URL，直接返回
  if (url.includes('/api/proxy/image/')) {
    return url;
  }
  
  // 如果是HTTP URL，使用代理
  if (url.startsWith('http')) {
    try {
      const encodedUrl = encodeURIComponent(url);
      return `${apiBaseUrl}/api/proxy/image/?url=${encodedUrl}`;
    } catch (e) {
      console.error('處理代理URL時出錯:', e);
      return '/images/no-image.png';
    }
  }
  
  // 其他情況，直接使用formatImageUrl
  return formatImageUrl(url);
} 