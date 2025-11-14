"""
Pain Validator Agent - Phase 4

Validates software needs by finding pain signals in LOCAL forums and communities
in each region, using their language and cultural platforms.

For each opportunity:
1. Finds local forum equivalents (not just Reddit)
2. Translates category keywords to local language
3. Searches for pain signals, frustrations, feature requests
4. Measures pain intensity (0-10)
5. Returns validated need score

Examples:
- Poland: Wykop (Polish Reddit)
- Romania: Reddit Romania, local business forums
- Japan: 2channel, 5channel
- Thailand: Pantip (Thai forum)
- Indonesia: Kaskus
- Germany: Gutefrage, Reddit Germany
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import Database

logger = logging.getLogger(__name__)


class PainValidatorAgent:
    """
    Validates market need by finding pain signals in local communities

    This is critical - finds ACTUAL demand in target markets
    """

    def __init__(self, config: Dict[str, Any], db: Database):
        self.config = config
        self.db = db

        # Local forum/community platforms per region
        self.local_forums = self._get_local_forums()

        # Keywords for pain signal detection
        self.pain_keywords = self._get_pain_keywords()

        logger.info("Pain Validator Agent initialized")

    def _get_local_forums(self) -> Dict[str, List[Dict]]:
        """
        Map of local forums and communities per region

        These are where locals ACTUALLY discuss problems and needs
        """
        return {
            # Eastern Europe
            'Poland': [
                {'name': 'Wykop', 'url': 'wykop.pl', 'type': 'social_news', 'language': 'Polish'},
                {'name': 'Reddit Poland', 'url': 'reddit.com/r/Polska', 'type': 'forum', 'language': 'Polish'},
                {'name': 'Forum Biznes', 'url': 'biznes.interia.pl/forum', 'type': 'business_forum', 'language': 'Polish'}
            ],
            'Romania': [
                {'name': 'Reddit Romania', 'url': 'reddit.com/r/Romania', 'type': 'forum', 'language': 'Romanian'},
                {'name': 'Softpedia Forum', 'url': 'forum.softpedia.com', 'type': 'tech_forum', 'language': 'Romanian'},
                {'name': 'Antreprenor.ro', 'url': 'antreprenor.ro/forum', 'type': 'business_forum', 'language': 'Romanian'}
            ],
            'Czech Republic': [
                {'name': 'Lupa.cz', 'url': 'lupa.cz', 'type': 'tech_news', 'language': 'Czech'},
                {'name': 'Reddit Czech', 'url': 'reddit.com/r/czech', 'type': 'forum', 'language': 'Czech'}
            ],

            # Asia
            'Japan': [
                {'name': '5channel (5ch)', 'url': '5ch.net', 'type': 'forum', 'language': 'Japanese'},
                {'name': 'Yahoo! Japan Chiebukuro', 'url': 'chiebukuro.yahoo.co.jp', 'type': 'q_and_a', 'language': 'Japanese'},
                {'name': 'Reddit Japan', 'url': 'reddit.com/r/japan', 'type': 'forum', 'language': 'English/Japanese'}
            ],
            'South Korea': [
                {'name': 'Naver Cafe', 'url': 'cafe.naver.com', 'type': 'community', 'language': 'Korean'},
                {'name': 'DC Inside', 'url': 'dcinside.com', 'type': 'forum', 'language': 'Korean'},
                {'name': 'Clien', 'url': 'clien.net', 'type': 'tech_forum', 'language': 'Korean'}
            ],
            'Thailand': [
                {'name': 'Pantip', 'url': 'pantip.com', 'type': 'forum', 'language': 'Thai'},
                {'name': 'Reddit Thailand', 'url': 'reddit.com/r/Thailand', 'type': 'forum', 'language': 'English/Thai'}
            ],
            'Indonesia': [
                {'name': 'Kaskus', 'url': 'kaskus.co.id', 'type': 'forum', 'language': 'Indonesian'},
                {'name': 'Reddit Indonesia', 'url': 'reddit.com/r/indonesia', 'type': 'forum', 'language': 'Indonesian/English'}
            ],
            'India': [
                {'name': 'Reddit India', 'url': 'reddit.com/r/india', 'type': 'forum', 'language': 'English'},
                {'name': 'Quora India', 'url': 'quora.com', 'type': 'q_and_a', 'language': 'English'},
                {'name': 'Team-BHP', 'url': 'team-bhp.com', 'type': 'community', 'language': 'English'}
            ],
            'Singapore': [
                {'name': 'HardwareZone', 'url': 'hardwarezone.com.sg', 'type': 'forum', 'language': 'English'},
                {'name': 'Reddit Singapore', 'url': 'reddit.com/r/singapore', 'type': 'forum', 'language': 'English'}
            ],

            # Western Europe
            'Germany': [
                {'name': 'Gutefrage', 'url': 'gutefrage.net', 'type': 'q_and_a', 'language': 'German'},
                {'name': 'Reddit Germany', 'url': 'reddit.com/r/de', 'type': 'forum', 'language': 'German'},
                {'name': 'Heise Forum', 'url': 'heise.de/forum', 'type': 'tech_forum', 'language': 'German'}
            ],
            'United Kingdom': [
                {'name': 'Reddit UK', 'url': 'reddit.com/r/unitedkingdom', 'type': 'forum', 'language': 'English'},
                {'name': 'UKBusinessForums', 'url': 'ukbusinessforums.co.uk', 'type': 'business_forum', 'language': 'English'}
            ],
            'United States': [
                {'name': 'Reddit', 'url': 'reddit.com', 'type': 'forum', 'language': 'English'},
                {'name': 'Hacker News', 'url': 'news.ycombinator.com', 'type': 'tech_news', 'language': 'English'},
                {'name': 'Indie Hackers', 'url': 'indiehackers.com', 'type': 'startup_community', 'language': 'English'}
            ]
        }

    def _get_pain_keywords(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Pain signal keywords per category, translated to local languages

        These indicate frustration, need, or feature gaps
        """
        return {
            'Project Management': {
                'English': ['project management tool', 'task tracking sucks', 'need better PM software',
                           'project tracking problem', 'team collaboration issue', 'alternative to'],
                'Polish': ['narzędzie do zarządzania projektami', 'problem ze śledzeniem zadań',
                          'potrzebuję lepszego oprogramowania PM'],
                'Romanian': ['instrument de management proiecte', 'problemă urmărire sarcini',
                            'software mai bun pentru PM'],
                'Japanese': ['プロジェクト管理ツール', 'タスク管理', '課題管理システム'],
                'Thai': ['โปรแกรมบริหารโครงการ', 'ติดตามงาน', 'จัดการทีม'],
                'Indonesian': ['alat manajemen proyek', 'tracking tugas', 'software PM'],
                'German': ['Projektmanagement-Tool', 'Aufgabenverfolgung', 'PM-Software'],
                'Korean': ['프로젝트 관리 도구', '작업 추적', '협업 도구']
            },
            'Construction Management': {
                'English': ['construction software', 'project tracking construction', 'building management',
                           'contractor management', 'construction planning tool'],
                'Polish': ['oprogramowanie budowlane', 'zarządzanie budową', 'planowanie konstrukcji'],
                'Romanian': ['software construcții', 'management șantier', 'planificare construcție'],
                'German': ['Bausoftware', 'Baustellenverwaltung', 'Bauplanung'],
                'Thai': ['ซอฟต์แวร์ก่อสร้าง', 'บริหารโครงการก่อสร้าง'],
                'Indonesian': ['software konstruksi', 'manajemen proyek konstruksi']
            },
            'HR & Payroll': {
                'English': ['HR software', 'payroll system', 'employee management', 'HR tool problem',
                           'payroll headache', 'time tracking'],
                'Polish': ['oprogramowanie HR', 'system płacowy', 'zarządzanie pracownikami'],
                'Romanian': ['software HR', 'sistem salarizare', 'management angajați'],
                'Japanese': ['人事管理システム', '給与計算', '勤怠管理'],
                'Thai': ['โปรแกรม HR', 'ระบบเงินเดือน', 'จัดการพนักงาน'],
                'Indonesian': ['software HR', 'sistem payroll', 'manajemen karyawan'],
                'German': ['HR-Software', 'Lohnabrechnungssystem', 'Mitarbeiterverwaltung'],
                'Korean': ['인사관리 시스템', '급여 관리', '직원 관리']
            },
            'Coworking & Space Management': {
                'English': ['coworking management', 'desk booking system', 'workspace software',
                           'coworking space problem', 'booking tool'],
                'Polish': ['zarządzanie coworkingiem', 'rezerwacja biurek', 'oprogramowanie dla przestrzeni'],
                'Romanian': ['management coworking', 'rezervare birouri', 'software spații lucru'],
                'Japanese': ['コワーキング管理', 'デスク予約', 'ワークスペース管理'],
                'Thai': ['บริหารพื้นที่ทำงาน', 'จองโต๊ะทำงาน'],
                'Korean': ['코워킹 관리', '책상 예약', '공유 오피스']
            },
            'Manufacturing & Supply Chain': {
                'English': ['manufacturing software', 'supply chain management', 'production planning',
                           'inventory problem', 'MES system'],
                'Polish': ['oprogramowanie produkcyjne', 'zarządzanie łańcuchem dostaw'],
                'Romanian': ['software producție', 'management lanț aprovizionare'],
                'German': ['Fertigungssoftware', 'Supply Chain Management', 'Produktionsplanung'],
                'Japanese': ['製造管理システム', 'サプライチェーン', '生産管理'],
                'Korean': ['제조 관리 시스템', '공급망 관리', '생산 계획']
            }
        }

    async def validate_all_opportunities(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate all opportunities with pain signals and contracts

        This is the deep validation that proves demand exists
        """

        logger.info(f"\n{'='*80}")
        logger.info(f"VALIDATING {len(opportunities)} OPPORTUNITIES")
        logger.info(f"{'='*80}\n")

        validated = []

        for i, opp in enumerate(opportunities, 1):
            logger.info(f"[{i}/{len(opportunities)}] Validating: {opp['source_product_name']} → {opp['target_region']}")

            # Validate this opportunity
            validation_result = await self._validate_opportunity(opp)

            # Add validation to opportunity
            opp.update(validation_result)

            # Store in database
            try:
                self.db.insert_opportunity(opp)
            except Exception as e:
                logger.error(f"Failed to update opportunity: {e}")

            validated.append(opp)

            # Log result
            need_score = validation_result.get('need_validated_score', 0)
            logger.info(f"  Need Score: {need_score}/10")
            logger.info(f"  Pain Signals: {validation_result.get('pain_signal_count', 0)}")
            logger.info(f"  Contracts: {validation_result.get('contract_count', 0)}")

        self.db.conn.commit()

        logger.info(f"\n✅ Validated {len(validated)} opportunities")

        return validated

    async def _validate_opportunity(
        self,
        opportunity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a single opportunity with:
        1. Pain signals from local forums
        2. Government contracts
        3. Job market signals
        4. Overall need score
        """

        target_region = opportunity['target_region']
        category = opportunity['source_category']

        # Step 1: Find pain signals in local forums
        pain_signals = await self._find_pain_signals(target_region, category)

        # Step 2: Search for government contracts (placeholder)
        contracts = await self._find_contracts(target_region, category)

        # Step 3: Calculate need score
        need_score = self._calculate_need_score(pain_signals, contracts)

        # Step 4: Determine market readiness
        market_readiness = self._assess_market_readiness(
            pain_signals, contracts, opportunity
        )

        return {
            'need_validated': need_score >= 6.0,
            'need_validated_score': need_score,
            'pain_signals': pain_signals,
            'pain_signal_count': len(pain_signals.get('signals', [])),
            'contract_validation': contracts,
            'contract_count': len(contracts.get('contracts', [])),
            'market_readiness': market_readiness,
            'validation_timestamp': datetime.now().isoformat()
        }

    async def _find_pain_signals(
        self,
        region: str,
        category: str
    ) -> Dict[str, Any]:
        """
        Find pain signals in local forums for this region and category

        Searches local language forums for frustration, needs, feature requests
        """

        logger.info(f"    Searching pain signals in {region} for {category}...")

        # Get forums for this region
        forums = self.local_forums.get(region, [])
        if not forums:
            logger.warning(f"    No local forums configured for {region}")
            return {'signals': [], 'total_mentions': 0, 'avg_pain_intensity': 0}

        # Get keywords for this category
        keywords_by_lang = self.pain_keywords.get(category, {})

        # Collect pain signals
        all_signals = []

        for forum in forums[:2]:  # Top 2 forums per region (for performance)
            language = forum.get('language', 'English')
            keywords = keywords_by_lang.get(language, keywords_by_lang.get('English', []))

            logger.debug(f"      Searching {forum['name']} ({language})")

            # TODO: In production, this would actually search the forum
            # For now, simulate finding signals
            signals = self._simulate_forum_search(forum, keywords, category, region)

            all_signals.extend(signals)

        # Calculate average pain intensity
        avg_pain = sum(s.get('pain_intensity', 0) for s in all_signals) / max(len(all_signals), 1)

        result = {
            'signals': all_signals,
            'total_mentions': len(all_signals),
            'avg_pain_intensity': round(avg_pain, 2),
            'forums_searched': [f['name'] for f in forums[:2]]
        }

        logger.info(f"      Found {len(all_signals)} pain signals (avg intensity: {avg_pain:.1f}/10)")

        return result

    def _simulate_forum_search(
        self,
        forum: Dict,
        keywords: List[str],
        category: str,
        region: str
    ) -> List[Dict[str, Any]]:
        """
        Simulate searching a forum for pain signals

        TODO: Replace with actual web scraping/API calls
        """

        # Simulate finding signals based on region and category
        # High-need combinations get more signals
        high_need_combos = {
            ('Poland', 'Construction Management'): 8,
            ('Romania', 'Construction Management'): 7,
            ('Thailand', 'Manufacturing & Supply Chain'): 6,
            ('Indonesia', 'HR & Payroll'): 7,
            ('India', 'Project Management'): 9,
            ('India', 'Construction Management'): 8
        }

        signal_count = high_need_combos.get((region, category), 2)

        signals = []
        for i in range(signal_count):
            signals.append({
                'source': forum['name'],
                'source_url': f"https://{forum['url']}/example-thread-{i}",
                'title': f"Need better {category} solution",
                'content': f"Looking for {category.lower()} software, current tools don't work well",
                'pain_intensity': 6.0 + (i * 0.5),  # 6.0-9.5 range
                'language': forum['language'],
                'posted_date': '2024-11-01',
                'upvotes': 15 + (i * 5),
                'comments': 8 + (i * 2)
            })

        return signals

    async def _find_contracts(
        self,
        region: str,
        category: str
    ) -> Dict[str, Any]:
        """
        Find government contracts in this region for this category

        Evidence of government spending = validated demand
        """

        logger.info(f"    Searching contracts in {region} for {category}...")

        # TODO: In production, scrape actual government procurement sites
        # For now, simulate contract discovery

        # High-value categories in specific regions
        contract_counts = {
            ('Poland', 'Construction Management'): 12,
            ('Romania', 'Construction Management'): 8,
            ('India', 'Construction Management'): 25,
            ('Thailand', 'Manufacturing & Supply Chain'): 6,
            ('Indonesia', 'HR & Payroll'): 4
        }

        count = contract_counts.get((region, category), 0)

        contracts = []
        total_value = 0

        for i in range(count):
            value = 50000 + (i * 25000)  # $50K-$500K range
            total_value += value

            contracts.append({
                'contract_id': f'{region}-{category}-{i}',
                'title': f'{category} System Procurement',
                'value': value,
                'department': 'Public Works' if 'Construction' in category else 'Administration',
                'deadline': '2025-03-01',
                'status': 'open',
                'url': f'https://procurement.example.{region.lower()}/contract-{i}'
            })

        result = {
            'contracts': contracts,
            'total_value': total_value,
            'contract_count': len(contracts)
        }

        if contracts:
            logger.info(f"      Found {len(contracts)} contracts (${total_value:,} total)")

        return result

    def _calculate_need_score(
        self,
        pain_signals: Dict,
        contracts: Dict
    ) -> float:
        """
        Calculate need validation score (0-10)

        Based on:
        - Pain signal count and intensity
        - Government contract demand
        - Community engagement
        """

        # Pain signal component (0-6 points)
        pain_count = pain_signals.get('total_mentions', 0)
        pain_intensity = pain_signals.get('avg_pain_intensity', 0)

        if pain_count == 0:
            pain_component = 0
        elif pain_count < 3:
            pain_component = pain_intensity * 0.3  # Low confidence
        elif pain_count < 7:
            pain_component = pain_intensity * 0.5  # Medium confidence
        else:
            pain_component = pain_intensity * 0.6  # High confidence

        # Contract component (0-4 points)
        contract_count = contracts.get('contract_count', 0)
        contract_value = contracts.get('total_value', 0)

        if contract_count == 0:
            contract_component = 0
        elif contract_count < 3:
            contract_component = 1.5
        elif contract_count < 10:
            contract_component = 2.5
        else:
            contract_component = 4.0

        # High-value contracts boost score
        if contract_value > 500000:
            contract_component += 1.0

        # Total score (0-10)
        total_score = min(10, pain_component + contract_component)

        return round(total_score, 2)

    def _assess_market_readiness(
        self,
        pain_signals: Dict,
        contracts: Dict,
        opportunity: Dict
    ) -> str:
        """
        Assess if market is ready for this solution

        Returns: ready, developing, early, not_ready
        """

        pain_count = pain_signals.get('total_mentions', 0)
        contract_count = contracts.get('contract_count', 0)
        competition = opportunity.get('target_competition_level', 0)

        # Ready: Pain + contracts + low competition
        if pain_count >= 5 and contract_count >= 3 and competition <= 2:
            return 'ready'

        # Developing: Some pain, some contracts
        elif pain_count >= 3 or contract_count >= 1:
            return 'developing'

        # Early: Minimal signals but gap exists
        elif pain_count >= 1 or contract_count >= 1:
            return 'early'

        # Not ready: No signals
        else:
            return 'not_ready'


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Pain Validator Agent ready")
