#
#   Copyright 2026 Hopsworks AB
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from hopsworks_apigen import public
from hsml.client.exceptions import ModelServingException
from hsml.schema import Schema
from hsml.utils.schema.column import Column


if TYPE_CHECKING:
    from hsfs.feature_view import FeatureView


# region Input categories

INPUT_CATEGORIES = (
    "serving_keys",
    "inference_helpers",
    "passed_features",
    "request_parameters",
)


# endregion


@public
class DeploymentSchema:
    """Schema describing a [`Deployment`][hsml.deployment.Deployment]'s inputs and labels.

    Captures four input categories that a prediction request must populate:
    serving keys to look up online feature vectors, inference helper columns
    fetched alongside the vector, features the client supplies directly to
    bypass online lookup, and additional request parameters consumed by
    on-demand or model-dependent transformations.
    The output schema mirrors the feature view's labels.
    """

    def __init__(
        self,
        serving_keys: list[dict[str, str]] | list[Column] | None = None,
        inference_helpers: list[dict[str, str]] | list[Column] | None = None,
        passed_features: list[dict[str, str]] | list[Column] | None = None,
        request_parameters: list[dict[str, str]] | list[Column] | None = None,
        output_schema: Schema | None = None,
        **kwargs,
    ):
        raw = {
            "serving_keys": serving_keys,
            "inference_helpers": inference_helpers,
            "passed_features": passed_features,
            "request_parameters": request_parameters,
        }
        normalized: dict[str, list[Column]] = {}
        seen: dict[str, str] = {}
        for category in INPUT_CATEGORIES:
            cols = _normalize_category(category, raw[category])
            for col in cols:
                if col.name in seen and seen[col.name] != category:
                    raise ValueError(
                        f"Name {col.name!r} appears in multiple input categories: "
                        f"{seen[col.name]} and {category}"
                    )
                seen[col.name] = category
            normalized[category] = sorted(cols, key=lambda c: c.name)
        self._serving_keys = normalized["serving_keys"]
        self._inference_helpers = normalized["inference_helpers"]
        self._passed_features = normalized["passed_features"]
        self._request_parameters = normalized["request_parameters"]
        self._output_schema = output_schema

    @public
    @property
    def serving_keys(self) -> list[Column]:
        """Serving keys required to look up feature vectors online."""
        return self._serving_keys

    @public
    @property
    def inference_helpers(self) -> list[Column]:
        """Inference helper columns fetched alongside the feature vector."""
        return self._inference_helpers

    @public
    @property
    def passed_features(self) -> list[Column]:
        """Feature view features the client supplies directly, bypassing online lookup."""
        return self._passed_features

    @public
    @property
    def request_parameters(self) -> list[Column]:
        """Additional request parameters consumed by transformations."""
        return self._request_parameters

    @public
    @property
    def output_schema(self) -> Schema | None:
        """Schema of the feature view's labels."""
        return self._output_schema

    @public
    @property
    def input_schema(self) -> dict[str, Any]:
        """Combined input dictionary across all four categories.

        Use [`DeploymentSchema.to_dict`][hsml.deployment_schema.DeploymentSchema.to_dict]
        for the full serialized schema including the output.
        """
        return {"columnar_schema": self._columnar_schema()}

    def _columnar_schema(self) -> list[dict[str, list[dict[str, str]]]]:
        result = []
        for category in INPUT_CATEGORIES:
            cols = getattr(self, "_" + category)
            if cols:
                result.append({category: [_column_to_dict(c) for c in cols]})
        return result

    def json(self) -> str:
        """Return the schema as a JSON string.

        Returns:
            JSON-encoded representation of the schema.
        """
        return json.dumps(self._build_dict(), indent=2)

    @public
    def to_dict(self) -> dict[str, Any]:
        """Get dict representation of the DeploymentSchema.

        Returns:
            JSON-serializable dictionary with ``columnar_schema`` and ``output_schema`` keys.
        """
        return self._build_dict()

    def _build_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"columnar_schema": self._columnar_schema()}
        if self._output_schema is not None:
            out["output_schema"] = self._output_schema.to_dict()
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeploymentSchema:
        """Rebuild a DeploymentSchema from its dict representation.

        Parameters:
            data: Dictionary produced by [`to_dict`][hsml.deployment_schema.DeploymentSchema.to_dict].

        Returns:
            A DeploymentSchema with the same input categories and output schema.
        """
        kwargs: dict[str, Any] = {}
        for bucket in data.get("columnar_schema", []) or []:
            for category, entries in bucket.items():
                if category in INPUT_CATEGORIES:
                    kwargs[category] = entries
        if "output_schema" in data and data["output_schema"]:
            output = data["output_schema"]
            cols = (
                (output.get("columnar_schema") or [])
                if isinstance(output, dict)
                else []
            )
            kwargs["output_schema"] = Schema(cols) if cols else None
        return cls(**kwargs)

    @classmethod
    def from_feature_view(
        cls,
        feature_view: FeatureView,
        passed_features: dict[str, str] | list[str] | None = None,
        request_parameters: dict[str, str] | None = None,
    ) -> DeploymentSchema:
        """Infer a DeploymentSchema from a feature view.

        Serving keys, inference helpers, and on-demand request parameters are
        derived from the feature view.
        ``passed_features`` must be supplied explicitly; auto-derivation is not
        performed in v1.
        ``request_parameters`` adds extra typed parameters (e.g.
        model-dependent transformation inputs) on top of the on-demand ones
        the feature view already declares.

        Parameters:
            feature_view: Feature view linked to the model being deployed.
            passed_features: Names (or name-to-type map) of FV features the caller will supply directly at predict time.
            request_parameters: Extra typed request parameters on top of the FV's on-demand ones.

        Returns:
            DeploymentSchema with all four input categories populated and an output schema derived from the FV labels.
        """
        if feature_view is None:
            raise ModelServingException(
                "Deployment schema inference requires the model to have a feature view"
            )

        feature_types = _feature_type_map(feature_view)
        fg_feature_types = _feature_group_type_map(feature_view)

        # serving_keys: prefix-strip then look up in the FV feature map; fall
        # back to the source feature group when the join key is not selected
        # into the FV itself.
        serving_key_entries: list[dict[str, str]] = []
        for sk in feature_view.serving_keys or []:
            display_name = sk.required_serving_key
            raw_name = sk.feature_name
            type_str = (
                feature_types.get(display_name)
                or feature_types.get(raw_name)
                or fg_feature_types.get((_fg_id(sk), raw_name))
            )
            if not type_str:
                raise ModelServingException(
                    f"Could not resolve type for serving key {display_name!r}; "
                    "supply an explicit DeploymentSchema."
                )
            serving_key_entries.append({"name": display_name, "type": type_str})

        # inference_helpers
        inference_helper_entries: list[dict[str, str]] = []
        for name in feature_view.inference_helper_columns or []:
            type_str = feature_types.get(name)
            if not type_str:
                raise ModelServingException(
                    f"Could not resolve type for inference helper {name!r}."
                )
            inference_helper_entries.append({"name": name, "type": type_str})

        # passed_features (explicit-only)
        passed_feature_entries = _resolve_passed_features(
            passed_features, feature_types
        )

        # request_parameters: union of on-demand FV params (defaulted to
        # "string") and explicit caller-provided typed params (which win).
        request_param_entries = _resolve_request_parameters(
            feature_view, request_parameters
        )

        # output_schema from labels
        output_schema = _build_output_schema(feature_view, feature_types)

        return cls(
            serving_keys=serving_key_entries,
            inference_helpers=inference_helper_entries,
            passed_features=passed_feature_entries,
            request_parameters=request_param_entries,
            output_schema=output_schema,
        )

    def __repr__(self) -> str:
        return (
            f"DeploymentSchema(serving_keys={len(self._serving_keys)}, "
            f"inference_helpers={len(self._inference_helpers)}, "
            f"passed_features={len(self._passed_features)}, "
            f"request_parameters={len(self._request_parameters)})"
        )


# region Helpers


def _column_to_dict(column: Column) -> dict[str, str]:
    out = {"name": column.name, "type": column.type}
    description = getattr(column, "description", None)
    if description is not None:
        out["description"] = description
    return out


def _normalize_category(
    category: str,
    values: list[dict[str, str]] | list[Column] | None,
) -> list[Column]:
    from hsfs.feature import is_ofs_type

    if values is None:
        return []
    cols: list[Column] = []
    seen: set[str] = set()
    for entry in values:
        if isinstance(entry, Column):
            name = getattr(entry, "name", None)
            type_str = entry.type
        elif isinstance(entry, dict):
            if "name" not in entry or entry["name"] is None:
                raise ValueError(f"Missing 'name' in {category} entry: {entry!r}")
            if "type" not in entry or entry["type"] is None:
                raise ValueError(f"Missing 'type' in {category} entry: {entry!r}")
            name = entry["name"]
            type_str = entry["type"]
        else:
            raise TypeError(
                f"{category} entry must be a dict or Column, got {type(entry).__name__}"
            )
        if name in seen:
            raise ValueError(f"Duplicate name {name!r} in category {category!r}")
        if not is_ofs_type(type_str):
            raise ValueError(f"{category} entry {name!r} has non-OFS type {type_str!r}")
        seen.add(name)
        cols.append(Column(type_str, name=name))
    return cols


def _feature_type_map(feature_view) -> dict[str, str]:
    from hsfs.feature import to_online_type

    return {
        f.name: to_online_type(f)
        for f in (feature_view.features or [])
        if to_online_type(f)
    }


def _feature_group_type_map(feature_view) -> dict[tuple[int | None, str], str]:
    from hsfs.feature import to_online_type

    out: dict[tuple[int | None, str], str] = {}
    for f in feature_view.features or []:
        fg = getattr(f, "feature_group", None)
        if fg is None:
            continue
        fg_id = getattr(fg, "id", None)
        fg_features = getattr(fg, "features", None) or []
        for fg_feature in fg_features:
            t = to_online_type(fg_feature)
            if t is not None:
                out[(fg_id, fg_feature.name)] = t
    return out


def _fg_id(serving_key) -> int | None:
    fg = getattr(serving_key, "feature_group", None)
    return getattr(fg, "id", None) if fg is not None else None


def _resolve_passed_features(
    passed_features: dict[str, str] | list[str] | None,
    feature_types: dict[str, str],
) -> list[dict[str, str]]:
    if not passed_features:
        return []
    if isinstance(passed_features, dict):
        return [{"name": n, "type": t} for n, t in passed_features.items()]
    entries: list[dict[str, str]] = []
    for name in passed_features:
        type_str = feature_types.get(name)
        if not type_str:
            raise ModelServingException(
                f"Could not resolve type for passed feature {name!r}; "
                "pass a {name: type} dict instead."
            )
        entries.append({"name": name, "type": type_str})
    return entries


def _resolve_request_parameters(
    feature_view,
    request_parameters: dict[str, str] | None,
) -> list[dict[str, str]]:
    explicit = request_parameters or {}
    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    for name in feature_view.request_parameters or []:
        if name in explicit:
            entries.append({"name": name, "type": explicit[name]})
        else:
            entries.append({"name": name, "type": "string"})
        seen.add(name)
    for name, type_str in explicit.items():
        if name not in seen:
            entries.append({"name": name, "type": type_str})
            seen.add(name)
    return entries


def _build_output_schema(feature_view, feature_types) -> Schema | None:
    labels = feature_view.labels or []
    if not labels:
        return None
    label_cols: list[dict[str, str]] = []
    for name in labels:
        type_str = feature_types.get(name)
        if not type_str:
            raise ModelServingException(
                f"Could not resolve type for label {name!r}; "
                "supply an explicit output_schema."
            )
        label_cols.append({"name": name, "type": type_str})
    return Schema(label_cols)


# endregion
