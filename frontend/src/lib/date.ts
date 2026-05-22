function parseUtcDate(value: string): Date {
  const hasTimezone = /(?:Z|[+-]\d{2}:\d{2})$/.test(value);

  return new Date(hasTimezone ? value : `${value}Z`);
}

export function formatDateTimeJst(value: string): string {
  const date = parseUtcDate(value);

  const parts = new Intl.DateTimeFormat("ja-JP", {
    timeZone: "Asia/Tokyo",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).formatToParts(date);

  const getPart = (type: Intl.DateTimeFormatPartTypes): string => {
    return parts.find((part) => part.type === type)?.value ?? "";
  };

  return `${getPart("year")}/${getPart("month")}/${getPart("day")} ${getPart("hour")}:${getPart("minute")}`;
}