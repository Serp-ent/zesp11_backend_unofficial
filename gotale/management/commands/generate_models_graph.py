# your_app/management/commands/sharp_graph_models.py

import pygraphviz as pgv
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Model


class Command(BaseCommand):
    help = (
        "Generates a model diagram with UML-compliant arrows, ignoring abstract models"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="model_graph.png",
            help="Output file name (default: model_graph.png)",
        )
        parser.add_argument(
            "--layout",
            type=str,
            default="dot",
            help="Layout engine (e.g., dot, neato, fdp)",
        )
        parser.add_argument(
            "--ranksep",
            type=float,
            default=1.5,
            help="Vertical spacing between nodes (default: 1.5)",
        )
        parser.add_argument(
            "--nodesep",
            type=float,
            default=1.0,
            help="Horizontal spacing between nodes (default: 1.0)",
        )
        parser.add_argument(
            "--fontsize",
            type=int,
            default=10,
            help="Font size for edge labels (default: 10)",
        )
        parser.add_argument(
            "--splines",
            type=str,
            default="polyline",
            help="Edge style (default: polyline)",
        )

    def handle(self, *args, **options):
        output_file = options["output"]
        layout_engine = options["layout"]
        ranksep = options["ranksep"]
        nodesep = options["nodesep"]
        fontsize = options["fontsize"]
        splines = options["splines"]

        # Initialize graph with improved styling
        graph = pgv.AGraph(
            directed=True,
            strict=False,
            rankdir="TB",
            splines=splines,
            ranksep=ranksep,
            nodesep=nodesep,
            concentrate="false",
            pad="0.5",
        )

        # Set default node and edge properties
        graph.node_attr.update(
            {
                "shape": "plaintext",
                "fontname": "Arial",
                "fontsize": "10",
            }
        )

        graph.edge_attr.update(
            {
                "fontname": "Arial",
                "fontsize": str(fontsize),
                "fontcolor": "black",
            }
        )

        # Collect concrete models only
        models = [
            model
            for model in apps.get_models()
            if not model._meta.abstract and not model._meta.proxy
        ]

        # Add nodes (models) with enhanced styling
        model_colors = self.get_model_colors(models)

        for model in models:
            label = self.get_model_label(model, model_colors[model._meta.label])
            node_attrs = {
                "label": label,
            }

            graph.add_node(model._meta.label, **node_attrs)

        # Add edges (relationships) with UML-compliant styling
        for model in models:
            for field in model._meta.get_fields():
                if field.related_model and field.related_model in models:
                    edge_style = self.get_uml_edge_style(field)
                    # Create the edge
                    graph.add_edge(
                        model._meta.label, field.related_model._meta.label, **edge_style
                    )

        # Generate and save graph
        graph.layout(prog=layout_engine)
        graph.draw(output_file)
        self.stdout.write(self.style.SUCCESS(f"Graph saved to {output_file}"))

    def get_model_label(self, model: Model, color: str) -> str:
        """Generate an HTML table label for the model with organized fields."""
        # Start with the table
        label = '<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">'

        # Model name row with color
        label += f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><B>{model._meta.label}</B></TD></TR>'

        # Add ID fields first with a different background
        id_fields = [
            (field.name, field.get_internal_type())
            for field in model._meta.fields
            if field.primary_key or field.name.endswith("_id")
        ]

        for field_name, field_type in id_fields:
            label += f'<TR><TD BGCOLOR="#E6E6FA">{field_name}</TD><TD BGCOLOR="#E6E6FA">{field_type}</TD></TR>'

        # Add other fields
        other_fields = [
            (field.name, field.get_internal_type())
            for field in model._meta.fields
            if not (field.primary_key or field.name.endswith("_id"))
        ]

        for field_name, field_type in other_fields:
            label += f"<TR><TD>{field_name}</TD><TD>{field_type}</TD></TR>"

        # Close the table
        label += "</TABLE>>"

        return label

    def get_model_colors(self, models):
        """Assign consistent colors to models based on their app."""
        app_colors = {
            "auth": "#B0E0E6",  # PowderBlue
            "admin": "#98FB98",  # PaleGreen
            "contenttypes": "#FFFACD",  # LemonChiffon
            "sessions": "#FFB6C1",  # LightPink
            "default": "#D3D3D3",  # LightGray
        }

        model_colors = {}
        for model in models:
            app_label = model._meta.app_label
            model_colors[model._meta.label] = app_colors.get(
                app_label, app_colors["default"]
            )

        return model_colors

    def get_uml_edge_style(self, field):
        """Determine UML-compliant edge styling based on field type."""
        # Get the relationship name
        rel_name = ""
        if hasattr(field, "related_name") and field.related_name:
            rel_name = field.related_name
        elif hasattr(field, "name"):
            rel_name = field.name

        # Default style for associations
        styles = {
            "color": "#333333",  # Dark gray for better contrast
            "label": f" {rel_name} ",
            "labelfontcolor": "darkblue",
            "labelfontname": "Arial",
            "penwidth": "1.5",
        }

        # Customize based on relationship type using UML conventions
        if field.many_to_many:
            # Many-to-Many: Solid line with plain arrowhead
            styles.update(
                {
                    "arrowhead": "normal",
                    "arrowsize": "1.0",
                    "style": "solid",
                    "label": f" {rel_name} (M:N) ",
                }
            )
        elif field.one_to_many:
            # One-to-Many: Solid line with diamond arrowhead (composition)
            styles.update(
                {
                    "arrowhead": "diamond",
                    "arrowsize": "1.2",
                    "style": "solid",
                    "label": f" {rel_name} (1:N) ",
                }
            )
        elif field.one_to_one:
            # One-to-One: Solid line with triangle arrowhead
            styles.update(
                {
                    "arrowhead": "vee",
                    "arrowsize": "1.0",
                    "style": "solid",
                    "label": f" {rel_name} (1:1) ",
                }
            )
        elif (
            hasattr(field, "get_internal_type")
            and field.get_internal_type() == "ForeignKey"
        ):
            # ForeignKey: Solid line with triangle arrowhead (association)
            styles.update(
                {
                    "arrowhead": "vee",
                    "arrowsize": "1.0",
                    "style": "solid",
                    "label": f" {rel_name} (FK) ",
                }
            )
        else:
            # Default association
            styles.update(
                {
                    "arrowhead": "vee",
                    "arrowsize": "1.0",
                    "style": "solid",
                }
            )

        return styles
