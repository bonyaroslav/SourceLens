import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TagModule } from 'primeng/tag';
import { TextareaModule } from 'primeng/textarea';

import { ImportSourceRequest } from '../../core/api/workspace-api.types';
import { ImportPanelViewModel } from '../workspace.models';

interface ImportFormModel {
  path: FormControl<string>;
  name: FormControl<string>;
  description: FormControl<string>;
}

@Component({
  selector: 'app-import-form',
  imports: [ReactiveFormsModule, ButtonModule, InputTextModule, TagModule, TextareaModule],
  template: `
    <form class="import-strip import-form" [formGroup]="form" (ngSubmit)="onSubmit()">
      <div class="field-block">
        <label class="section-label" for="source-path">Local file or folder path</label>
        <input
          id="source-path"
          pInputText
          formControlName="path"
          placeholder="C:\\Users\\me\\Documents\\notes.md"
        />
      </div>

      <div class="field-grid">
        <div class="field-block">
          <label class="section-label" for="source-name">Display name</label>
          <input
            id="source-name"
            pInputText
            formControlName="name"
            placeholder="Optional override"
          />
        </div>

        <div class="field-block">
          <label class="section-label" for="source-description">Description</label>
          <textarea
            id="source-description"
            pTextarea
            autoResize
            rows="2"
            formControlName="description"
            placeholder="Optional source note"
          ></textarea>
        </div>
      </div>

      <div class="question-shell__footer">
        <p>
          The backend imports directly from the local filesystem, so this MVP uses a path-based form
          instead of browser upload.
        </p>

        <button
          pButton
          type="submit"
          label="Queue import"
          icon="pi pi-plus"
          severity="secondary"
          [outlined]="true"
          [loading]="importState.pending"
        ></button>
      </div>
    </form>

    @if (showPathError) {
      <p class="form-feedback is-error">A local file or folder path is required.</p>
    }

    @if (importState.error) {
      <p class="form-feedback is-error">{{ importState.error }}</p>
    }

    @if (importState.statusLabel) {
      <div class="import-job-status">
        <div class="import-job-status__meta">
          <span class="section-label">Latest job</span>
          <p-tag [value]="importState.statusLabel" [severity]="importState.statusSeverity"></p-tag>
        </div>

        @if (importState.statusDetail) {
          <p>{{ importState.statusDetail }}</p>
        }

        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">Source id</span>
            <strong>{{ importState.sourceId ?? 'Pending' }}</strong>
          </div>
          <div class="detail-item">
            <span class="detail-label">Job id</span>
            <strong>{{ importState.jobId ?? 'Pending' }}</strong>
          </div>
        </div>
      </div>
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ImportFormComponent {
  @Input({ required: true }) importState!: ImportPanelViewModel;
  @Output() readonly submitImport = new EventEmitter<ImportSourceRequest>();

  readonly form = new FormGroup<ImportFormModel>({
    path: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    name: new FormControl('', { nonNullable: true }),
    description: new FormControl('', { nonNullable: true }),
  });

  get showPathError(): boolean {
    const pathControl = this.form.controls.path;

    return pathControl.invalid && (pathControl.dirty || pathControl.touched);
  }

  onSubmit(): void {
    if (this.form.invalid) {
      this.form.controls.path.markAsTouched();
      return;
    }

    const { path, name, description } = this.form.getRawValue();
    this.submitImport.emit({
      path: path.trim(),
      name: toOptionalValue(name),
      description: toOptionalValue(description),
    });
  }
}

function toOptionalValue(value: string): string | null {
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}
