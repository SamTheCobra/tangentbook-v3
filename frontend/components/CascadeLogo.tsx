export default function CascadeLogo({ height = 36 }: { height?: number }) {
  const markWidth = height * 0.9;
  const barH = height * 0.14;
  const gap = height * 0.25;
  const barGap = barH * 0.6;

  return (
    <div style={{
      display: "inline-flex",
      alignItems: "center",
      gap: `${gap}px`,
      lineHeight: 1,
    }}>
      {/* Cascading bars mark */}
      <div style={{
        display: "flex",
        flexDirection: "column",
        gap: `${barGap}px`,
        justifyContent: "center",
      }}>
        <div style={{ width: `${markWidth}px`, height: `${barH}px`, background: "white" }} />
        <div style={{ width: `${markWidth * 0.67}px`, height: `${barH}px`, background: "white", alignSelf: "flex-end" }} />
        <div style={{ width: `${markWidth * 0.33}px`, height: `${barH}px`, background: "white", alignSelf: "flex-end" }} />
      </div>
      {/* Wordmark */}
      <span style={{
        fontFamily: "'Syne', sans-serif",
        fontWeight: 800,
        fontSize: `${height * 0.6}px`,
        color: "white",
        letterSpacing: "0.02em",
        lineHeight: 1,
      }}>CASCADE</span>
    </div>
  );
}
