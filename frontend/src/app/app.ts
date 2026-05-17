import { Component } from '@angular/core';

import { WorkspaceShellComponent } from './workspace/components/workspace-shell.component';

@Component({
  selector: 'app-root',
  imports: [WorkspaceShellComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {}
