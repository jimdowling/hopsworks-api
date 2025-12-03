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

import { BaseClient, ClientConfig } from './client/base';
import { Project } from './project';
import { ProjectApi } from './api/projectApi';

export interface ConnectionOptions {
  host: string;
  port?: number;
  apiKey?: string;
  hostnameVerification?: boolean;
  project?: string;
}

/**
 * A Hopsworks connection object.
 *
 * This class provides methods to connect to Hopsworks and access projects.
 *
 * @example
 * ```typescript
 * import { connection } from '@hopsworks/api';
 *
 * const conn = await connection({
 *   host: 'my-instance.cloud.hopsworks.ai',
 *   port: 443,
 *   apiKey: 'your-api-key'
 * });
 * ```
 */
export class Connection {
  private client: BaseClient;
  private projectApi: ProjectApi;
  private connected: boolean = false;
  private options: ConnectionOptions;

  constructor(options: ConnectionOptions) {
    this.options = options;

    const clientConfig: ClientConfig = {
      host: options.host,
      port: options.port || 443,
      apiKey: options.apiKey,
      hostnameVerification: options.hostnameVerification ?? true,
    };

    this.client = new BaseClient(clientConfig);
    this.projectApi = new ProjectApi(this.client);
  }

  /**
   * Establishes the connection to Hopsworks.
   */
  async connect(): Promise<void> {
    if (this.connected) {
      return;
    }

    if (this.options.project) {
      this.client.setProjectName(this.options.project);
    }

    this.connected = true;
  }

  /**
   * Get an existing project.
   *
   * @param name - The name of the project. If not provided, uses the project name from connection options.
   * @returns A Project object
   *
   * @example
   * ```typescript
   * const project = await conn.getProject('my_project');
   * ```
   */
  async getProject(name?: string): Promise<Project> {
    if (!this.connected) {
      await this.connect();
    }

    const projectName = name || this.options.project;
    if (!projectName) {
      throw new Error(
        'No project name provided. Please provide a project name or set a project when creating the connection.'
      );
    }

    const projectData = await this.projectApi.getProject(projectName);
    return new Project(projectData, this.client);
  }

  /**
   * Get all accessible projects.
   *
   * @returns An array of Project objects
   */
  async getProjects(): Promise<Project[]> {
    if (!this.connected) {
      await this.connect();
    }

    const projects = await this.projectApi.getProjects();
    return projects.map((p) => new Project(p, this.client));
  }

  /**
   * Check if a project exists.
   *
   * @param name - The name of the project
   * @returns True if the project exists, false otherwise
   */
  async projectExists(name: string): Promise<boolean> {
    if (!this.connected) {
      await this.connect();
    }

    return await this.projectApi.exists(name);
  }

  /**
   * Close the connection gracefully.
   */
  close(): void {
    this.connected = false;
  }
}

/**
 * Connection factory function.
 *
 * @param options - Connection options
 * @returns A connected Connection object
 *
 * @example
 * ```typescript
 * import { connection } from '@hopsworks/api';
 *
 * const conn = await connection({
 *   host: 'my-instance.cloud.hopsworks.ai',
 *   apiKey: 'your-api-key',
 *   project: 'my_project'
 * });
 *
 * const project = await conn.getProject();
 * ```
 */
export async function connection(options: ConnectionOptions): Promise<Connection> {
  const conn = new Connection(options);
  await conn.connect();
  return conn;
}
