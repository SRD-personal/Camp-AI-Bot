#!/usr/bin/env python3
"""
Add sample KIT content to knowledge base for testing
This can be run even without internet access to external sites
"""
import asyncio
import sys
import uuid
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import AsyncSessionLocal
from app.models.document import Document
from app.models.document import KnowledgeChunk
from app.services.document_service import DocumentService
from sqlalchemy import select, delete

# Sample KIT content
SAMPLE_CONTENT = [
    {
        "title": "About Kalaimagal Institute of Technology",
        "description": "Overview of KIT",
        "content": """
Kalaimagal Institute of Technology (KIT) is a premier engineering college located in Tamil Nadu, India.
Established with the vision of providing quality technical education, KIT offers undergraduate and
postgraduate programs in various engineering disciplines.

The institute is approved by AICTE (All India Council for Technical Education) and affiliated with
Anna University, Chennai. KIT is committed to academic excellence, research, and innovation.

Our mission is to develop technically competent engineers who can contribute to society and industry
with their skills and knowledge. We focus on holistic development of students through academics,
extracurricular activities, and industry exposure.
        """
    },
    {
        "title": "Departments and Programs",
        "description": "Academic departments at KIT",
        "content": """
KIT offers the following undergraduate (B.E/B.Tech) programs:

1. Computer Science and Engineering (CSE)
   - Focus on software development, algorithms, data structures, and emerging technologies
   - Strong placement record with top IT companies

2. Electronics and Communication Engineering (ECE)
   - Covers embedded systems, VLSI, signal processing, and communication systems
   - Well-equipped labs for practical learning

3. Electrical and Electronics Engineering (EEE)
   - Power systems, control systems, and renewable energy
   - Industry collaborations for internships and projects

4. Mechanical Engineering
   - CAD/CAM, robotics, thermal engineering, and manufacturing
   - Modern workshops and fabrication facilities

5. Civil Engineering
   - Structural engineering, transportation, and environmental engineering
   - Field visits and practical exposure to construction sites

Postgraduate programs (M.E/M.Tech) are also offered in selected specializations.
        """
    },
    {
        "title": "Campus Facilities",
        "description": "Infrastructure and facilities at KIT",
        "content": """
KIT provides world-class infrastructure and facilities:

Academic Facilities:
- Modern classrooms with smart boards and projectors
- Well-stocked central library with digital resources
- High-speed internet connectivity across campus
- Computer labs with latest software and hardware
- Department-specific laboratories for practical training

Student Amenities:
- Separate hostels for boys and girls
- Sports facilities including cricket ground, volleyball, basketball courts
- Indoor games room with table tennis, chess, carrom
- Cafeteria serving hygienic and nutritious food
- Medical facilities with qualified staff
- Transport facility from major locations

Research & Innovation:
- Innovation lab for student projects
- Research centers in emerging technologies
- Collaboration with industries for sponsored projects
- Regular workshops and seminars by industry experts
        """
    },
    {
        "title": "Admissions Process",
        "description": "How to apply to KIT",
        "content": """
Admissions to KIT are based on merit and entrance exam scores.

For B.E/B.Tech Programs:
- Students must have completed 10+2 with Physics, Chemistry, and Mathematics
- Admission through Tamil Nadu Engineering Admissions (TNEA) based on 10+2 marks
- Alternatively, through management quota seats (limited)
- Minimum eligibility: 50% aggregate in 10+2 (45% for reserved categories)

For M.E/M.Tech Programs:
- Bachelor's degree in relevant engineering discipline
- Valid GATE score preferred
- Anna University entrance exam for non-GATE applicants

Application Process:
1. Visit KIT official website or TNEA counseling portal
2. Register and fill application form
3. Upload required documents (marksheets, certificates, photos)
4. Pay application fee online
5. Submit application before deadline
6. Attend counseling as per schedule
7. Document verification and seat allotment

Important Dates:
- Applications open: Usually in May/June
- Last date: As per TNEA schedule
- Counseling: June-July
- Classes begin: August

For detailed information, contact the admissions office or visit the official website.
        """
    },
    {
        "title": "Placements and Career Services",
        "description": "Placement cell and career support",
        "content": """
KIT has a dedicated Training and Placement Cell that works year-round to ensure excellent career
opportunities for students.

Placement Highlights:
- 85%+ placement rate across all departments
- Top recruiters include TCS, Infosys, Wipro, Cognizant, L&T, Ashok Leyland
- Highest package: 12 LPA (2023-24)
- Average package: 4.5 LPA
- 100+ companies visit campus annually

Pre-Placement Training:
- Aptitude and reasoning classes from 3rd semester
- Communication skills and personality development
- Technical interview preparation
- Mock interviews and group discussions
- Resume building workshops
- Coding competitions and hackathons

Internships:
- Mandatory internship in final year
- Industry internships arranged through college
- Summer internship programs in 3rd year
- Project-based learning with industry mentors

Alumni Network:
- Strong alumni network across globe
- Regular alumni meetups and networking events
- Alumni mentorship program for students
- Support in higher education guidance

The placement cell also assists with:
- Higher education opportunities (MS, MBA)
- Competitive exam preparation (GATE, GRE, CAT)
- Entrepreneurship development programs
        """
    },
    {
        "title": "Contact Information",
        "description": "How to reach KIT",
        "content": """
Kalaimagal Institute of Technology

Address:
Kalaimagal Institute of Technology
Vellore-Chittoor Main Road
Chitheri, Madhanur Post
Tamil Nadu - 635301
India

Contact:
Phone: +91-XXXX-XXXXXX (Admissions Office)
Email: admissions@kitcbe.com
Website: https://kitcbe.com

For specific inquiries:
- Admissions: admissions@kitcbe.com
- Placements: placements@kitcbe.com
- General: info@kitcbe.com

Office Hours:
Monday to Friday: 9:00 AM - 5:00 PM
Saturday: 9:00 AM - 1:00 PM
Sunday: Closed

How to Reach:
By Road: Well connected by road from Chennai (180 km), Bangalore (160 km), and Vellore (35 km)
By Train: Nearest railway station - Katpadi Junction (40 km)
By Air: Nearest airport - Chennai International Airport (180 km)

Campus Visits:
Prospective students and parents are welcome to visit the campus.
Prior appointment recommended. Contact admissions office to schedule a visit.
        """
    }
]


async def clear_sample_documents():
    """Clear all existing sample documents from knowledge base"""
    print("Clearing existing sample documents...")

    async with AsyncSessionLocal() as db:
        try:
            # Delete all chunks for sample documents (file_type='web' with 'sample_' prefix)
            stmt = delete(KnowledgeChunk).where(
                KnowledgeChunk.document_id.in_(
                    select(Document.id).where(Document.file_name.like('sample_%'))
                )
            )
            result = await db.execute(stmt)
            chunks_deleted = result.rowcount

            # Delete all sample documents
            stmt = delete(Document).where(Document.file_name.like('sample_%'))
            result = await db.execute(stmt)
            docs_deleted = result.rowcount

            await db.commit()

            print(f"✓ Deleted {docs_deleted} sample documents and {chunks_deleted} chunks\n")

        except Exception as e:
            print(f"✗ Failed to clear existing documents: {str(e)}\n")
            await db.rollback()
            raise


async def populate_sample_content(skip_existing: bool = True):
    """Populate knowledge base with sample KIT content"""
    print("=" * 70)
    print("Adding Sample KIT Content to Knowledge Base")
    print("=" * 70)
    if skip_existing:
        print("Deduplication enabled: Will skip existing documents")
    print()

    added_count = 0
    skipped_count = 0

    async with AsyncSessionLocal() as db:
        doc_service = DocumentService(db)

        for idx, sample in enumerate(SAMPLE_CONTENT, 1):
            print(f"[{idx}/{len(SAMPLE_CONTENT)}] Processing: {sample['title']}")

            try:
                # Check if sample already exists (deduplication)
                file_name = f"sample_{idx}.txt"

                if skip_existing:
                    stmt = select(Document).where(Document.file_name == file_name)
                    result = await db.execute(stmt)
                    existing_doc = result.scalar_one_or_none()

                    if existing_doc:
                        print(f"  ⏭️  Skipping (already exists): {sample['title']}")
                        skipped_count += 1
                        continue

                # Create document
                document = Document(
                    id=uuid.uuid4(),
                    title=sample['title'],
                    description=sample['description'],
                    file_name=file_name,
                    file_type='web',
                    file_size=len(sample['content']),
                    status='processing',
                    department='general'
                )
                db.add(document)
                await db.commit()
                await db.refresh(document)

                # Process content
                await doc_service.process_document_content(
                    document_id=document.id,
                    content=sample['content'].strip(),
                    file_type='sample'
                )

                # Update status
                document.status = 'ready'
                await db.commit()

                added_count += 1
                print(f"  ✓ Added: {sample['title']}")

            except Exception as e:
                print(f"  ✗ Failed: {sample['title']} - {str(e)}")
                await db.rollback()
                continue

    print()
    print("=" * 70)
    print(f"✓ Added {added_count} new documents")
    print(f"✓ Skipped {skipped_count} existing documents")
    print("=" * 70)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Add sample KIT content to knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Normal run (skip existing)
  python add_sample_content.py

  # Clear existing sample documents before adding
  python add_sample_content.py --clear-existing

  # Allow duplicates (don't skip existing)
  python add_sample_content.py --allow-duplicates
        """
    )

    parser.add_argument(
        '--clear-existing',
        action='store_true',
        help='Delete all existing sample documents before adding (useful for refresh)'
    )

    parser.add_argument(
        '--allow-duplicates',
        action='store_true',
        help='Allow duplicate documents (by default, existing documents are skipped)'
    )

    args = parser.parse_args()

    # Run with options
    async def main():
        if args.clear_existing:
            await clear_sample_documents()

        await populate_sample_content(skip_existing=not args.allow_duplicates)

    asyncio.run(main())
