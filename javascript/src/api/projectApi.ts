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

import { BaseClient } from '../client/base';

export interface ProjectData {
  projectId: number;
  projectName: string;
  owner: string;
  description?: string;
  created?: string;
}

export class ProjectApi {
  constructor(private client: BaseClient) {}

  async getProject(name: string): Promise<ProjectData> {
    const response = await this.client['sendRequest']<{ items: ProjectData[] }>('GET', [
      'project',
      'getProjectInfo',
      name,
    ]);

    if (!response.items || response.items.length === 0) {
      throw new Error(`Project '${name}' not found`);
    }

    return response.items[0];
  }

  async getProjects(): Promise<ProjectData[]> {
    const response = await this.client['sendRequest']<{ items: ProjectData[] }>('GET', [
      'project',
    ]);
    return response.items || [];
  }

  async exists(name: string): Promise<boolean> {
    try {
      await this.getProject(name);
      return true;
    } catch (error) {
      return false;
    }
  }
}
