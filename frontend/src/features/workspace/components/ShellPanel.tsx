import { PropsWithChildren } from 'react';

type ShellPanelProps = PropsWithChildren<{
  eyebrow: string;
  title: string;
  body: string;
}>;

export function ShellPanel({ eyebrow, title, body, children }: ShellPanelProps) {
  return (
    <section className="shell-panel">
      <p className="shell-panel__eyebrow">{eyebrow}</p>
      <h2 className="shell-panel__title">{title}</h2>
      <p className="shell-panel__body">{body}</p>
      {children}
    </section>
  );
}
