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

export interface Feature {
  name: string;
  type: string;
  description?: string;
  primary?: boolean;
  partition?: boolean;
  hudiPrecombineKey?: boolean;
}

export interface FeatureGroupData {
  id: number;
  name: string;
  version: number;
  description: string;
  featurestoreId: number;
  featurestoreName: string;
  type: string;
  onlineEnabled: boolean;
  timeTravelFormat?: string;
  features: Feature[];
  primaryKey: string[];
  partitionKey: string[];
  eventTime?: string;
  created?: string;
}

export interface FeatureGroupCreateOptions {
  version?: number;
  description?: string;
  primaryKey?: string[];
  partitionKey?: string[];
  eventTime?: string;
  onlineEnabled?: boolean;
  featurestoreId: number;
  features?: Feature[];
}

export class FeatureGroupApi {
  constructor(private client: BaseClient, private featurestoreId: number) {}

  async get(name: string, version: number): Promise<FeatureGroupData> {
    const projectName = this.client.getProjectName();
    if (!projectName) {
      throw new Error('Project name not set');
    }

    const response = await this.client['sendRequest']<FeatureGroupData>('GET', [
      'project',
      projectName,
      'featurestores',
      this.featurestoreId,
      'featuregroups',
      name,
    ], {
      queryParams: { version },
    });

    return response;
  }

  async create(name: string, options: FeatureGroupCreateOptions): Promise<FeatureGroupData> {
    const projectName = this.client.getProjectName();
    if (!projectName) {
      throw new Error('Project name not set');
    }

    const payload = {
      name,
      version: options.version,
      description: options.description || '',
      features: options.features || [],
      primaryKey: options.primaryKey || [],
      partitionKey: options.partitionKey || [],
      eventTime: options.eventTime,
      onlineEnabled: options.onlineEnabled || false,
      type: 'cachedFeaturegroupDTO',
      timeTravelFormat: 'HUDI',
    };

    const response = await this.client['sendRequest']<FeatureGroupData>('POST', [
      'project',
      projectName,
      'featurestores',
      this.featurestoreId,
      'featuregroups',
    ], {
      data: payload,
    });

    return response;
  }

  async insertData(featureGroupId: number, data: Record<string, any>[], write: 'insert' | 'upsert' = 'upsert'): Promise<void> {
    const projectName = this.client.getProjectName();
    if (!projectName) {
      throw new Error('Project name not set');
    }

    const payload = {
      items: data,
    };

    await this.client['sendRequest']('POST', [
      'project',
      projectName,
      'featurestores',
      this.featurestoreId,
      'featuregroups',
      featureGroupId,
      'ingestion',
    ], {
      queryParams: { write },
      data: payload,
    });
  }
}
