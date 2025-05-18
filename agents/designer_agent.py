from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import json
import base64
from io import BytesIO
import altair as alt
from datetime import datetime

class ChartData(BaseModel):
    x: List[Union[str, float, int]]
    y: List[Union[float, int]]
    type: str = "line"
    name: Optional[str] = None
    color: Optional[str] = None

class DesignerRequest(BaseModel):
    chart_type: str  # line, bar, candlestick, pie, scatter
    title: str
    data: Union[List[ChartData], Dict[str, Any]]
    style: Optional[str] = "professional"  # professional, minimal, dark
    dimensions: Optional[Dict[str, int]] = {"width": 800, "height": 500}
    interactive: bool = True
    output_format: str = "html"  # html, png, svg

class DesignerResponse(BaseModel):
    visualization: str  # HTML string or base64 encoded image
    format: str
    metadata: Optional[Dict[str, Any]] = None

class DesignerAgent:
    """The Designer Agent creates visualizations to support the analysis.
    
    Main Steps:
    1. Initialization:
       - Sets up visualization libraries (Plotly, Altair)
       - Configures color schemes and templates for different styles
    2. Process:
       - Takes chart type, data, and style preferences
       - Selects appropriate visualization method
       - Applies styling and formatting
       - Handles interactive features if requested
       - Optimizes for specified dimensions
    3. Output:
       - Returns visualization in requested format (HTML, PNG, SVG)
       - Ensures responsive and accessible design
    """
    
    def __init__(self):
        # Color schemes for different styles
        self.color_schemes = {
            "professional": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
            "minimal": ["#4C72B0", "#55A868", "#C44E52", "#8172B3", "#CCB974"],
            "dark": ["#00FF00", "#FF0000", "#0000FF", "#FFFF00", "#FF00FF"]
        }
        
        # Chart templates
        self.templates = {
            "professional": "plotly_white",
            "minimal": "simple_white",
            "dark": "plotly_dark"
        }

    def _create_line_chart(self, data: List[ChartData], title: str, style: str) -> go.Figure:
        """Create a line chart using Plotly."""
        fig = go.Figure()
        
        for series in data:
            fig.add_trace(
                go.Scatter(
                    x=series.x,
                    y=series.y,
                    name=series.name or "",
                    line=dict(color=series.color)
                )
            )
            
        fig.update_layout(
            title=title,
            template=self.templates[style],
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig

    def _create_candlestick_chart(self, data: Dict[str, Any], title: str, style: str) -> go.Figure:
        """Create a candlestick chart for financial data."""
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=data["dates"],
                    open=data["open"],
                    high=data["high"],
                    low=data["low"],
                    close=data["close"]
                )
            ]
        )
        
        fig.update_layout(
            title=title,
            template=self.templates[style],
            xaxis_title="Date",
            yaxis_title="Price"
        )
        
        return fig

    def _create_comparison_chart(self, data: List[ChartData], title: str, style: str) -> go.Figure:
        """Create a comparison chart with multiple indicators."""
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=(title, "Volume")
        )
        
        for i, series in enumerate(data):
            fig.add_trace(
                go.Scatter(
                    x=series.x,
                    y=series.y,
                    name=series.name or f"Series {i+1}",
                    line=dict(color=series.color or self.color_schemes[style][i])
                ),
                row=1,
                col=1
            )
        
        fig.update_layout(
            template=self.templates[style],
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig

    def _convert_to_output_format(self, fig: go.Figure, format: str, dimensions: Dict[str, int]) -> str:
        """Convert Plotly figure to specified output format."""
        if format == "html":
            return fig.to_html(include_plotlyjs=True)
        elif format == "png":
            img_bytes = fig.to_image(
                format="png",
                width=dimensions["width"],
                height=dimensions["height"]
            )
            return base64.b64encode(img_bytes).decode()
        elif format == "svg":
            return fig.to_image(format="svg").decode()
        else:
            raise ValueError(f"Unsupported output format: {format}")

    async def process(self, request: DesignerRequest) -> DesignerResponse:
        """Process the request and generate visualization."""
        try:
            # Create appropriate chart based on type
            if request.chart_type == "line":
                fig = self._create_line_chart(
                    request.data if isinstance(request.data, list) else [request.data],
                    request.title,
                    request.style or "professional"
                )
            elif request.chart_type == "candlestick":
                fig = self._create_candlestick_chart(
                    request.data if isinstance(request.data, dict) else request.data[0].dict(),
                    request.title,
                    request.style or "professional"
                )
            elif request.chart_type == "comparison":
                fig = self._create_comparison_chart(
                    request.data if isinstance(request.data, list) else [request.data],
                    request.title,
                    request.style or "professional"
                )
            else:
                raise ValueError(f"Unsupported chart type: {request.chart_type}")

            # Update layout based on dimensions
            fig.update_layout(
                width=request.dimensions["width"],
                height=request.dimensions["height"]
            )

            # Convert to requested output format
            visualization = self._convert_to_output_format(
                fig,
                request.output_format,
                request.dimensions
            )

            return DesignerResponse(
                visualization=visualization,
                format=request.output_format,
                metadata={
                    "chart_type": request.chart_type,
                    "style": request.style,
                    "dimensions": request.dimensions,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        except Exception as e:
            return DesignerResponse(
                visualization="Error generating visualization",
                format="text",
                metadata={"error": str(e)}
            )

    @staticmethod
    def get_supported_chart_types() -> List[str]:
        """Return list of supported chart types."""
        return [
            "line",
            "candlestick",
            "comparison",
            "bar",
            "pie",
            "scatter"
        ]

    @staticmethod
    def get_supported_styles() -> List[str]:
        """Return list of supported visualization styles."""
        return [
            "professional",
            "minimal",
            "dark"
        ]
