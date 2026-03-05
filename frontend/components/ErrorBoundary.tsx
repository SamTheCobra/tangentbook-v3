"use client";

import { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div
            className="border p-4"
            style={{
              background: "var(--surface)",
              borderColor: "var(--border)",
            }}
          >
            <p
              className="text-xs"
              style={{
                color: "var(--text-muted)",
                fontFamily: "JetBrains Mono, monospace",
              }}
            >
              Component error: {this.state.error?.message || "Unknown error"}
            </p>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
