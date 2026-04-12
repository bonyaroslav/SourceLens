import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { TagModule } from 'primeng/tag';

import { SourceListItemViewModel } from '../workspace.models';

@Component({
  selector: 'app-source-list',
  imports: [TagModule],
  template: `
    @if (loading) {
      <p class="panel-empty">Loading sources from the backend...</p>
    } @else if (error) {
      <p class="panel-empty is-error">{{ error }}</p>
    } @else if (sources.length === 0) {
      <p class="panel-empty">
        No imported sources yet. Queue a file or folder path to create the first workspace source.
      </p>
    } @else {
      <div class="source-list">
        @for (source of sources; track source.id) {
          <article
            class="source-row"
            [class.is-active]="source.id === activeSourceId"
            tabindex="0"
            (click)="selectSource.emit(source.id)"
            (keydown.enter)="selectSource.emit(source.id)"
            (keydown.space)="selectSource.emit(source.id); $event.preventDefault()"
          >
            <div class="source-row__body">
              <div class="source-row__headline">
                <div>
                  <h3>{{ source.name }}</h3>
                  <p>{{ source.updatedLabel }}</p>
                </div>

                @if (source.id === activeSourceId) {
                  <span class="active-pill">Active</span>
                }
              </div>

              <p class="source-row__description">{{ source.description }}</p>

              <div class="source-row__meta">
                <span class="source-type">{{ source.typeLabel }}</span>
                <p-tag
                  [value]="source.statusLabel"
                  [severity]="source.statusSeverity"
                ></p-tag>
              </div>
            </div>
          </article>
        }
      </div>
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class SourceListComponent {
  @Input() sources: SourceListItemViewModel[] = [];
  @Input() activeSourceId: string | null = null;
  @Input() loading = false;
  @Input() error: string | null = null;
  @Output() readonly selectSource = new EventEmitter<string>();
}
