// Format currency with proper localization and decimal places
const CURRENCY_FORMATTER = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 8,
});

// Format percentage with proper decimal places
const PERCENT_FORMATTER = new Intl.NumberFormat('en-US', {
  style: 'percent',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

// Format large numbers with appropriate suffixes (K, M, B, T)
const COMPACT_NUMBER_FORMATTER = new Intl.NumberFormat('en-US', {
  maximumFractionDigits: 2,
  notation: 'compact',
  compactDisplay: 'short',
});

// Format date to a readable string
const DATE_FORMATTER = new Intl.DateTimeFormat('en-US', {
  year: 'numeric',
  month: 'short',
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hour12: true,
});

export const formatCurrency = (
  value: number | string,
  currency: string = 'USD'
): string => {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) return '$0.00';
  
  // For very small values, switch to scientific notation
  if (Math.abs(numValue) > 0 && Math.abs(numValue) < 0.0001) {
    return numValue.toExponential(4);
  }
  
  return CURRENCY_FORMATTER.format(numValue).replace('$', getCurrencySymbol(currency));
};

export const formatPercentage = (value: number | string): string => {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) return '0.00%';
  return PERCENT_FORMATTER.format(numValue / 100);
};

export const formatNumber = (value: number | string): string => {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) return '0';
  return COMPACT_NUMBER_FORMATTER.format(numValue);
};

export const formatDate = (date: Date | string | number): string => {
  try {
    const dateObj = typeof date === 'string' || typeof date === 'number' 
      ? new Date(date) 
      : date;
    
    if (isNaN(dateObj.getTime())) return 'Invalid Date';
    
    return DATE_FORMATTER.format(dateObj);
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid Date';
  }
};

export const formatTimeAgo = (date: Date | string | number): string => {
  try {
    const dateObj = typeof date === 'string' || typeof date === 'number' 
      ? new Date(date) 
      : date;
    
    if (isNaN(dateObj.getTime())) return 'Invalid Date';
    
    const seconds = Math.floor((Date.now() - dateObj.getTime()) / 1000);
    
    const intervals = {
      year: 31536000,
      month: 2592000,
      week: 604800,
      day: 86400,
      hour: 3600,
      minute: 60,
      second: 1,
    };
    
    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
      const interval = Math.floor(seconds / secondsInUnit);
      if (interval >= 1) {
        return interval === 1 
          ? `${interval} ${unit} ago` 
          : `${interval} ${unit}s ago`;
      }
    }
    
    return 'just now';
  } catch (error) {
    console.error('Error formatting time ago:', error);
    return 'Invalid Date';
  }
};

export const formatBytes = (bytes: number, decimals: number = 2): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
};

const getCurrencySymbol = (currency: string): string => {
  // Add more currency symbols as needed
  const symbols: Record<string, string> = {
    USD: '$',
    EUR: '€',
    GBP: '£',
    JPY: '¥',
    CNY: '¥',
    KRW: '₩',
    BTC: '₿',
    ETH: 'Ξ',
  };
  
  return symbols[currency.toUpperCase()] || `${currency} `;
};

// Format a number with commas as thousand separators
export const formatWithCommas = (value: number | string): string => {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) return '0';
  return numValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

// Truncate a string to a specified length and add ellipsis if needed
export const truncateString = (
  str: string,
  maxLength: number = 20,
  ellipsis: string = '...'
): string => {
  if (!str || str.length <= maxLength) return str;
  return `${str.substring(0, maxLength)}${ellipsis}`;
};
