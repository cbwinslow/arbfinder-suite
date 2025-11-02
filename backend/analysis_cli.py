#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Price Analysis CLI for ArbFinder Suite
Provides comprehensive tools for price adjustments, metadata management, and item tracking.
"""

import argparse
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from decimal import Decimal

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import track
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False


class PriceAnalyzer:
    """Advanced price analysis and adjustment engine."""
    
    CONDITION_MULTIPLIERS = {
        'new': 1.00,
        'like_new': 0.95,
        'excellent': 0.85,
        'very_good': 0.75,
        'good': 0.65,
        'fair': 0.50,
        'poor': 0.30
    }
    
    DAMAGE_TYPE_MULTIPLIERS = {
        'minor_scratch': 0.3,
        'dent': 0.7,
        'aesthetic': 1.0,
        'structural': 2.0,
        'rust': 1.5,
        'crack': 1.8,
        'discoloration': 0.4
    }
    
    LOCATION_MULTIPLIERS = {
        'front': 1.5,
        'passenger': 1.0,
        'rear': 0.8,
        'driver': 1.2,
        'top': 1.1,
        'bottom': 0.7,
        'side': 0.9
    }
    
    def calculate_linear_depreciation(
        self, 
        base_price: Decimal, 
        age_years: Decimal, 
        rate: Decimal = Decimal('0.10')
    ) -> Decimal:
        """Calculate linear depreciation."""
        factor = max(Decimal('0'), Decimal('1') - (age_years * rate))
        return base_price * factor
    
    def calculate_exponential_depreciation(
        self,
        base_price: Decimal,
        age_years: Decimal,
        half_life: Decimal = Decimal('2.5')
    ) -> Decimal:
        """Calculate exponential depreciation."""
        import math
        factor = Decimal(str(math.pow(0.5, float(age_years / half_life))))
        return base_price * factor
    
    def calculate_scurve_depreciation(
        self,
        base_price: Decimal,
        age_years: Decimal,
        appreciation_rate: Decimal = Decimal('0.02')
    ) -> Decimal:
        """Calculate S-curve depreciation/appreciation."""
        if age_years < 1:
            factor = Decimal('0.7') + (Decimal('0.3') * (Decimal('1') - age_years))
        elif age_years < 5:
            factor = Decimal('0.6') + (Decimal('0.1') * (Decimal('5') - age_years) / Decimal('4'))
        else:
            # Potential appreciation after 5 years
            factor = Decimal('0.5') + (appreciation_rate * (age_years - Decimal('5')))
        return base_price * factor
    
    def calculate_condition_adjustment(
        self,
        base_price: Decimal,
        condition: str
    ) -> Decimal:
        """Apply condition-based price adjustment."""
        multiplier = Decimal(str(self.CONDITION_MULTIPLIERS.get(condition.lower(), 0.75)))
        return base_price * multiplier
    
    def calculate_damage_adjustment(
        self,
        base_price: Decimal,
        damage_type: str,
        location: str = 'general',
        severity: str = 'minor'
    ) -> tuple[Decimal, Dict[str, Any]]:
        """
        Calculate price adjustment for specific damage.
        Returns: (adjusted_price, details_dict)
        """
        base_adjustment = Decimal('-0.10')  # -10% base
        
        damage_mult = Decimal(str(
            self.DAMAGE_TYPE_MULTIPLIERS.get(damage_type.lower(), 1.0)
        ))
        location_mult = Decimal(str(
            self.LOCATION_MULTIPLIERS.get(location.lower(), 1.0)
        ))
        
        severity_mult = {
            'minor': Decimal('0.5'),
            'moderate': Decimal('1.0'),
            'major': Decimal('1.5'),
            'severe': Decimal('2.0')
        }.get(severity.lower(), Decimal('1.0'))
        
        total_adjustment = base_adjustment * damage_mult * location_mult * severity_mult
        adjusted_price = base_price * (Decimal('1') + total_adjustment)
        
        details = {
            'base_adjustment': float(base_adjustment),
            'damage_multiplier': float(damage_mult),
            'location_multiplier': float(location_mult),
            'severity_multiplier': float(severity_mult),
            'total_adjustment_pct': float(total_adjustment * 100),
            'price_reduction': float(base_price - adjusted_price)
        }
        
        return adjusted_price, details
    
    def calculate_market_adjustment(
        self,
        base_price: Decimal,
        supply_count: int,
        demand_score: Decimal,
        recent_sales: int
    ) -> Decimal:
        """Calculate market-based price adjustment."""
        supply_factor = min(Decimal(str(supply_count)) / Decimal('50'), Decimal('2.0'))
        demand_factor = max(Decimal(str(recent_sales)) / Decimal('10'), Decimal('0.5'))
        
        if supply_factor > 0:
            market_adjustment = demand_factor / supply_factor
        else:
            market_adjustment = Decimal('1.0')
        
        # Apply bounds
        market_adjustment = max(Decimal('0.7'), min(Decimal('1.3'), market_adjustment))
        
        return base_price * market_adjustment
    
    def calculate_seasonal_adjustment(
        self,
        base_price: Decimal,
        item_category: str,
        current_month: int
    ) -> Decimal:
        """Calculate seasonal price adjustments."""
        seasonal_factors = {
            'winter_gear': {
                12: 1.3, 1: 1.3, 2: 1.2,  # High demand in winter
                6: 0.8, 7: 0.8, 8: 0.8    # Low demand in summer
            },
            'summer_gear': {
                6: 1.3, 7: 1.3, 8: 1.2,   # High demand in summer
                12: 0.8, 1: 0.8, 2: 0.8   # Low demand in winter
            },
            'back_to_school': {
                7: 1.15, 8: 1.2, 9: 1.1
            },
            'holiday_items': {
                11: 1.3, 12: 1.4
            }
        }
        
        factor = seasonal_factors.get(item_category, {}).get(current_month, 1.0)
        return base_price * Decimal(str(factor))
    
    def calculate_comprehensive_price(
        self,
        base_price: Decimal,
        age_years: Decimal,
        condition: str,
        damage_list: List[Dict] = None,
        supply_count: int = 50,
        recent_sales: int = 10,
        category: str = None,
        completeness_pct: Decimal = Decimal('100')
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive final price with all adjustments.
        Returns detailed breakdown.
        """
        result = {
            'base_price': float(base_price),
            'adjustments': []
        }
        
        # Age depreciation
        depreciated_price = self.calculate_exponential_depreciation(base_price, age_years)
        result['adjustments'].append({
            'type': 'age_depreciation',
            'factor': float(depreciated_price / base_price),
            'amount': float(base_price - depreciated_price),
            'description': f'{float(age_years):.1f} years old'
        })
        current_price = depreciated_price
        
        # Condition adjustment
        condition_price = self.calculate_condition_adjustment(current_price, condition)
        result['adjustments'].append({
            'type': 'condition',
            'factor': float(condition_price / current_price),
            'amount': float(current_price - condition_price),
            'description': f'Condition: {condition}'
        })
        current_price = condition_price
        
        # Damage adjustments
        if damage_list:
            for damage in damage_list:
                damaged_price, details = self.calculate_damage_adjustment(
                    current_price,
                    damage.get('type', 'aesthetic'),
                    damage.get('location', 'general'),
                    damage.get('severity', 'minor')
                )
                result['adjustments'].append({
                    'type': 'damage',
                    'factor': float(damaged_price / current_price),
                    'amount': float(current_price - damaged_price),
                    'description': f"{damage.get('severity')} {damage.get('type')} on {damage.get('location')}",
                    'details': details
                })
                current_price = damaged_price
        
        # Market adjustment
        market_price = self.calculate_market_adjustment(
            current_price, supply_count, Decimal('1.0'), recent_sales
        )
        result['adjustments'].append({
            'type': 'market',
            'factor': float(market_price / current_price),
            'amount': float(current_price - market_price),
            'description': f'Supply: {supply_count}, Recent sales: {recent_sales}'
        })
        current_price = market_price
        
        # Seasonal adjustment (if category provided)
        if category:
            current_month = datetime.now().month
            seasonal_price = self.calculate_seasonal_adjustment(
                current_price, category, current_month
            )
            result['adjustments'].append({
                'type': 'seasonal',
                'factor': float(seasonal_price / current_price),
                'amount': float(current_price - seasonal_price),
                'description': f'Seasonal factor for {category}'
            })
            current_price = seasonal_price
        
        # Completeness adjustment
        completeness_factor = completeness_pct / Decimal('100')
        complete_price = current_price * completeness_factor
        result['adjustments'].append({
            'type': 'completeness',
            'factor': float(completeness_factor),
            'amount': float(current_price - complete_price),
            'description': f'{float(completeness_pct)}% complete'
        })
        current_price = complete_price
        
        result['final_price'] = float(current_price)
        result['total_adjustment'] = float(base_price - current_price)
        result['total_adjustment_pct'] = float((base_price - current_price) / base_price * 100)
        
        return result


class MetadataManager:
    """Manage and generate item metadata."""
    
    @staticmethod
    def generate_metadata(item: Dict) -> Dict[str, Any]:
        """Generate enhanced metadata for an item."""
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'completeness_score': MetadataManager._calculate_completeness(item),
            'data_quality_score': MetadataManager._calculate_data_quality(item),
            'enrichment_sources': []
        }
        
        # Extract specifications from title/description
        specs = MetadataManager._extract_specifications(
            item.get('title', ''),
            item.get('description', '')
        )
        if specs:
            metadata['specifications'] = specs
            metadata['enrichment_sources'].append('text_extraction')
        
        # Generate tags
        tags = MetadataManager._generate_tags(item)
        if tags:
            metadata['tags'] = tags
            metadata['enrichment_sources'].append('auto_tagging')
        
        return metadata
    
    @staticmethod
    def _calculate_completeness(item: Dict) -> float:
        """Calculate data completeness score (0-100)."""
        required_fields = ['title', 'price', 'condition', 'source']
        optional_fields = ['description', 'images', 'category', 'metadata']
        
        required_score = sum(1 for f in required_fields if item.get(f)) / len(required_fields)
        optional_score = sum(1 for f in optional_fields if item.get(f)) / len(optional_fields)
        
        return round((0.7 * required_score + 0.3 * optional_score) * 100, 2)
    
    @staticmethod
    def _calculate_data_quality(item: Dict) -> float:
        """Calculate data quality score (0-100)."""
        score = 100.0
        
        # Penalize missing critical data
        if not item.get('title'):
            score -= 30
        elif len(item.get('title', '')) < 10:
            score -= 15
        
        if not item.get('description'):
            score -= 20
        elif len(item.get('description', '')) < 50:
            score -= 10
        
        if not item.get('condition'):
            score -= 15
        
        if not item.get('images'):
            score -= 10
        
        return max(0, score)
    
    @staticmethod
    def _extract_specifications(title: str, description: str) -> Dict[str, str]:
        """Extract specifications from text."""
        import re
        
        specs = {}
        text = f"{title} {description}".lower()
        
        # Common patterns
        patterns = {
            'year': r'(19|20)\d{2}',
            'size': r'(\d+)\s*(gb|tb|mb|inch|"|\')',
            'model': r'model\s+([a-z0-9-]+)',
            'brand': r'(samsung|apple|sony|dell|hp|lenovo|microsoft)',
            'color': r'(black|white|silver|blue|red|gold|gray|grey)',
            'condition': r'(new|used|refurbished|excellent|good|fair)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                specs[key] = match.group(0)
        
        return specs
    
    @staticmethod
    def _generate_tags(item: Dict) -> List[str]:
        """Generate tags for an item."""
        tags = []
        
        # Add category tags
        if category := item.get('category'):
            tags.append(category.lower())
        
        # Add condition tags
        if condition := item.get('condition'):
            tags.append(f"condition_{condition.lower()}")
        
        # Add price range tags
        if price := item.get('price'):
            if price < 50:
                tags.append('budget')
            elif price < 200:
                tags.append('mid_range')
            else:
                tags.append('premium')
        
        # Add source tag
        if source := item.get('source'):
            tags.append(f"source_{source.lower()}")
        
        return tags


def create_cli() -> argparse.ArgumentParser:
    """Create the advanced CLI parser."""
    parser = argparse.ArgumentParser(
        prog='arbfinder-analysis',
        description='Advanced Price Analysis CLI for ArbFinder Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Price calculation command
    price_parser = subparsers.add_parser('calculate', help='Calculate adjusted price')
    price_parser.add_argument('--base-price', type=float, required=True, help='Base price')
    price_parser.add_argument('--age', type=float, default=0, help='Age in years')
    price_parser.add_argument('--condition', default='good', help='Item condition')
    price_parser.add_argument('--damage', action='append', help='Damage: type:location:severity')
    price_parser.add_argument('--supply', type=int, default=50, help='Supply count')
    price_parser.add_argument('--sales', type=int, default=10, help='Recent sales count')
    price_parser.add_argument('--category', help='Item category for seasonal adjustment')
    price_parser.add_argument('--completeness', type=float, default=100, help='Completeness percentage')
    price_parser.add_argument('--output', choices=['json', 'table'], default='table', help='Output format')
    
    # Depreciation calculator
    deprec_parser = subparsers.add_parser('depreciation', help='Calculate depreciation')
    deprec_parser.add_argument('--base-price', type=float, required=True)
    deprec_parser.add_argument('--age', type=float, required=True)
    deprec_parser.add_argument('--model', choices=['linear', 'exponential', 's_curve'], default='exponential')
    deprec_parser.add_argument('--rate', type=float, help='Depreciation rate (for linear)')
    deprec_parser.add_argument('--half-life', type=float, help='Half-life years (for exponential)')
    
    # Damage assessment
    damage_parser = subparsers.add_parser('damage', help='Calculate damage impact')
    damage_parser.add_argument('--base-price', type=float, required=True)
    damage_parser.add_argument('--type', required=True, help='Damage type')
    damage_parser.add_argument('--location', default='general', help='Damage location')
    damage_parser.add_argument('--severity', default='minor', help='Damage severity')
    
    # Metadata generation
    meta_parser = subparsers.add_parser('metadata', help='Generate metadata')
    meta_parser.add_argument('--file', required=True, help='JSON file with item data')
    meta_parser.add_argument('--output', help='Output file (default: stdout)')
    
    # Batch processing
    batch_parser = subparsers.add_parser('batch', help='Batch process items')
    batch_parser.add_argument('--input', required=True, help='Input JSON file with items')
    batch_parser.add_argument('--output', required=True, help='Output JSON file')
    batch_parser.add_argument('--operation', choices=['price', 'metadata', 'both'], default='both')
    
    return parser


def format_price_result(result: Dict, output_format: str):
    """Format and display price calculation result."""
    if output_format == 'json':
        print(json.dumps(result, indent=2))
        return
    
    if RICH_AVAILABLE:
        # Create adjustments table
        table = Table(title="Price Adjustments")
        table.add_column("Type", style="cyan")
        table.add_column("Factor", style="yellow")
        table.add_column("Amount", style="red")
        table.add_column("Description", style="white")
        
        for adj in result['adjustments']:
            table.add_row(
                adj['type'],
                f"{adj['factor']:.4f}",
                f"${adj['amount']:.2f}",
                adj['description']
            )
        
        console.print(table)
        
        # Summary panel
        summary = f"""
Base Price:     ${result['base_price']:.2f}
Final Price:    ${result['final_price']:.2f}
Total Adj:      ${result['total_adjustment']:.2f} ({result['total_adjustment_pct']:.1f}%)
        """
        console.print(Panel(summary, title="Price Summary", border_style="green"))
    else:
        print(f"\n=== Price Calculation Result ===")
        print(f"Base Price: ${result['base_price']:.2f}")
        print(f"\nAdjustments:")
        for adj in result['adjustments']:
            print(f"  {adj['type']}: {adj['factor']:.4f} (${adj['amount']:.2f}) - {adj['description']}")
        print(f"\nFinal Price: ${result['final_price']:.2f}")
        print(f"Total Adjustment: ${result['total_adjustment']:.2f} ({result['total_adjustment_pct']:.1f}%)")


def main():
    """Main CLI entry point."""
    parser = create_cli()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    analyzer = PriceAnalyzer()
    
    if args.command == 'calculate':
        # Parse damage list
        damage_list = []
        if args.damage:
            for damage_str in args.damage:
                parts = damage_str.split(':')
                damage_list.append({
                    'type': parts[0] if len(parts) > 0 else 'aesthetic',
                    'location': parts[1] if len(parts) > 1 else 'general',
                    'severity': parts[2] if len(parts) > 2 else 'minor'
                })
        
        result = analyzer.calculate_comprehensive_price(
            Decimal(str(args.base_price)),
            Decimal(str(args.age)),
            args.condition,
            damage_list,
            args.supply,
            args.sales,
            args.category,
            Decimal(str(args.completeness))
        )
        
        format_price_result(result, args.output)
    
    elif args.command == 'depreciation':
        base_price = Decimal(str(args.base_price))
        age = Decimal(str(args.age))
        
        if args.model == 'linear':
            rate = Decimal(str(args.rate)) if args.rate else Decimal('0.10')
            result_price = analyzer.calculate_linear_depreciation(base_price, age, rate)
        elif args.model == 'exponential':
            half_life = Decimal(str(args.half_life)) if args.half_life else Decimal('2.5')
            result_price = analyzer.calculate_exponential_depreciation(base_price, age, half_life)
        else:  # s_curve
            result_price = analyzer.calculate_scurve_depreciation(base_price, age)
        
        print(f"Base Price: ${base_price:.2f}")
        print(f"Age: {age} years")
        print(f"Model: {args.model}")
        print(f"Depreciated Price: ${result_price:.2f}")
        print(f"Depreciation: ${base_price - result_price:.2f} ({float((base_price - result_price) / base_price * 100):.1f}%)")
    
    elif args.command == 'damage':
        base_price = Decimal(str(args.base_price))
        damaged_price, details = analyzer.calculate_damage_adjustment(
            base_price, args.type, args.location, args.severity
        )
        
        print(f"Base Price: ${base_price:.2f}")
        print(f"Damage: {args.severity} {args.type} on {args.location}")
        print(f"Adjusted Price: ${damaged_price:.2f}")
        print(f"Price Reduction: ${details['price_reduction']:.2f} ({details['total_adjustment_pct']:.1f}%)")
        print(f"\nBreakdown:")
        print(f"  Damage multiplier: {details['damage_multiplier']:.2f}")
        print(f"  Location multiplier: {details['location_multiplier']:.2f}")
        print(f"  Severity multiplier: {details['severity_multiplier']:.2f}")
    
    elif args.command == 'metadata':
        with open(args.file, 'r') as f:
            item = json.load(f)
        
        metadata = MetadataManager.generate_metadata(item)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(metadata, f, indent=2)
            print(f"Metadata written to {args.output}")
        else:
            print(json.dumps(metadata, indent=2))
    
    elif args.command == 'batch':
        with open(args.input, 'r') as f:
            items = json.load(f)
        
        results = []
        for item in track(items, description="Processing items...") if RICH_AVAILABLE else items:
            result = {'item': item}
            
            if args.operation in ['price', 'both']:
                price_result = analyzer.calculate_comprehensive_price(
                    Decimal(str(item.get('base_price', 100))),
                    Decimal(str(item.get('age_years', 0))),
                    item.get('condition', 'good'),
                    item.get('damage_list', []),
                    item.get('supply_count', 50),
                    item.get('recent_sales', 10),
                    item.get('category'),
                    Decimal(str(item.get('completeness_pct', 100)))
                )
                result['price_analysis'] = price_result
            
            if args.operation in ['metadata', 'both']:
                metadata = MetadataManager.generate_metadata(item)
                result['metadata'] = metadata
            
            results.append(result)
        
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Processed {len(results)} items. Results written to {args.output}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
