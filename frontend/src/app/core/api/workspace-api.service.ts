import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import {
  AskResponseDto,
  AskSourceRequest,
  ImportJobDto,
  ImportSourceRequest,
  ImportSubmissionDto,
  SourceDto,
} from './workspace-api.types';

@Injectable({ providedIn: 'root' })
export class WorkspaceApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api';

  listSources(): Observable<SourceDto[]> {
    return this.http.get<SourceDto[]>(`${this.baseUrl}/sources`);
  }

  getSource(sourceId: string): Observable<SourceDto> {
    return this.http.get<SourceDto>(`${this.baseUrl}/sources/${sourceId}`);
  }

  submitImport(request: ImportSourceRequest): Observable<ImportSubmissionDto> {
    return this.http.post<ImportSubmissionDto>(`${this.baseUrl}/sources/import`, request);
  }

  getImportJob(jobId: string): Observable<ImportJobDto> {
    return this.http.get<ImportJobDto>(`${this.baseUrl}/import-jobs/${jobId}`);
  }

  askSource(sourceId: string, request: AskSourceRequest): Observable<AskResponseDto> {
    return this.http.post<AskResponseDto>(`${this.baseUrl}/sources/${sourceId}/ask`, request);
  }
}
