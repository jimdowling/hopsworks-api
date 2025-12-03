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

import { BaseClient } from './client/base';
import { ProjectData } from './api/projectApi';
import { FeatureStore } from './featureStore';
import { FeatureStoreApi } from './api/featureStoreApi';

/**
 * Represents a Hopsworks project.
 */
export class Project {
  public readonly id: number;
  public readonly name: string;
  public readonly owner: string;
  public readonly description?: string;
  public readonly created?: string;

  private featureStoreApi: FeatureStoreApi;

  constructor(data: ProjectData, private client: BaseClient) {
    this.id = data.projectId;
    this.name = data.projectName;
    this.owner = data.owner;
    this.description = data.description;
    this.created = data.created;

    this.featureStoreApi = new FeatureStoreApi(this.client);
  }

  /**
   * Connect to the project's Feature Store.
   *
   * Defaulting to the project's default feature store.
   * To get a shared feature store, provide the project name of the feature store.
   *
   * @param name - The name of the feature store (defaults to the project name)
   * @returns A FeatureStore object
   *
   * @example
   * ```typescript
   * const fs = await project.getFeatureStore();
   * ```
   */
  async getFeatureStore(name?: string): Promise<FeatureStore> {
    const featureStoreName = name || `${this.name}_featurestore`;
    const fsData = await this.featureStoreApi.get(featureStoreName);
    return new FeatureStore(fsData, this.client);
  }

  toString(): string {
    return `Project(${this.name}, ${this.owner}${
      this.description ? `, ${this.description}` : ''
    })`;
  }
}
