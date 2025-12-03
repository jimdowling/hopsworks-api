/**
 * Copyright 2024 Hopsworks AB
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiKeyAuth } from './auth';

export interface ClientConfig {
  host: string;
  port?: number;
  apiKey?: string;
  hostnameVerification?: boolean;
}

export class RestAPIError extends Error {
  constructor(
    public url: string,
    public status: number,
    public statusText: string,
    public data: any
  ) {
    super(`REST API Error: ${status} ${statusText} - ${url}`);
    this.name = 'RestAPIError';
  }
}

export class BaseClient {
  protected baseUrl: string;
  protected client: AxiosInstance;
  protected auth?: ApiKeyAuth;
  protected projectName?: string;

  constructor(config: ClientConfig) {
    const port = config.port || 443;
    const protocol = port === 443 ? 'https' : 'http';
    this.baseUrl = `${protocol}://${config.host}:${port}`;

    this.client = axios.create({
      baseURL: this.baseUrl,
      headers: {
        'Content-Type': 'application/json',
      },
      httpsAgent: config.hostnameVerification === false ? { rejectUnauthorized: false } : undefined,
    });

    if (config.apiKey) {
      this.auth = new ApiKeyAuth(config.apiKey);
      this.client.interceptors.request.use((requestConfig) => {
        if (this.auth) {
          requestConfig.headers.Authorization = `ApiKey ${this.auth.token}`;
        }
        return requestConfig;
      });
    }

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response) {
          throw new RestAPIError(
            error.config.url,
            error.response.status,
            error.response.statusText,
            error.response.data
          );
        }
        throw error;
      }
    );
  }

  protected async sendRequest<T = any>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    pathParams: (string | number)[],
    options: {
      queryParams?: Record<string, any>;
      data?: any;
      headers?: Record<string, string>;
      withBasePath?: boolean;
    } = {}
  ): Promise<T> {
    const { queryParams, data, headers, withBasePath = true } = options;

    const basePathParams = withBasePath ? ['hopsworks-api', 'api'] : [];
    const fullPath = [...basePathParams, ...pathParams].join('/');

    const config: AxiosRequestConfig = {
      method,
      url: `/${fullPath}`,
      params: queryParams,
      data,
      headers,
    };

    const response: AxiosResponse<T> = await this.client.request(config);
    return response.data;
  }

  public setProjectName(projectName: string): void {
    this.projectName = projectName;
  }

  public getProjectName(): string | undefined {
    return this.projectName;
  }
}
