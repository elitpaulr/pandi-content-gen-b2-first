# Quality Assurance (QA) Functionality Guide

## Overview

The QA (Quality Assurance) functionality allows human annotators to review and approve/reject different elements of generated B2 First Reading Part 5 tasks. This ensures quality control and helps maintain high standards for exam content.

## Features

### 🔍 QA Review Interface

The QA review interface provides a comprehensive annotation system for:

- **Overall Task**: General assessment of the entire task
- **Title**: Review of task title appropriateness and clarity
- **Text**: Evaluation of reading text quality, length, and level
- **Individual Questions**: Assessment of each question's quality and correctness

### ✅ Annotation Options

For each element, annotators can:

- **Status Selection**: Choose from "Pending", "Approved", or "Rejected"
- **Reviewer Name**: Record who performed the review
- **Notes**: Add detailed comments and feedback
- **Timestamp**: Automatic recording of review time

## How to Use the QA System

### 1. Access QA Review

1. Navigate to the **Task Library** tab
2. Select either "Individual Tasks" or "Batch Collections"
3. Choose **"🔍 QA Review"** from the View Mode dropdown
4. Select a task to review

### 2. Perform QA Review

1. **Enter Reviewer Name**: Required field to identify the reviewer
2. **Review Task Overview**: Check basic metrics (word count, questions, etc.)
3. **Annotate Each Element**:
   - Overall Task: General quality assessment
   - Title: Appropriateness and clarity
   - Text: Content quality, length, language level
   - Questions: Individual question quality and correctness

### 3. Add Detailed Notes

For each element, provide specific feedback:
- **Approved**: Note what works well
- **Rejected**: Explain specific issues and suggestions for improvement
- **Pending**: Note what needs further review

### 4. Save Annotations

Click **"💾 Save QA Annotations"** to:
- Update the task JSON file with QA data
- Record timestamp and reviewer information
- Generate QA summary statistics

## QA Annotation Structure

### JSON Format

QA annotations are stored in the task JSON file under the `qa_annotations` field:

```json
{
  "qa_annotations": {
    "overall_task": {
      "status": "approved|rejected|pending",
      "reviewer": "Reviewer Name",
      "notes": "Detailed feedback",
      "timestamp": "2025-06-15T10:30:00.000Z"
    },
    "title": {
      "status": "approved|rejected|pending",
      "reviewer": "Reviewer Name", 
      "notes": "Title-specific feedback",
      "timestamp": "2025-06-15T10:30:00.000Z"
    },
    "text": {
      "status": "approved|rejected|pending",
      "reviewer": "Reviewer Name",
      "notes": "Text quality feedback",
      "timestamp": "2025-06-15T10:30:00.000Z"
    },
    "questions": {
      "question_1": {
        "status": "approved|rejected|pending",
        "reviewer": "Reviewer Name",
        "notes": "Question-specific feedback",
        "timestamp": "2025-06-15T10:30:00.000Z"
      }
      // ... additional questions
    }
  }
}
```

## QA Review Guidelines

### Overall Task Assessment

**Approve if:**
- Task meets B2 First standards
- Content is age-appropriate and culturally neutral
- Overall structure is coherent
- Questions test appropriate skills

**Reject if:**
- Content is inappropriate or biased
- Task doesn't meet exam standards
- Major structural issues
- Significant quality problems

### Title Review

**Approve if:**
- Clear and engaging
- Accurately reflects content
- Appropriate length
- Professional tone

**Reject if:**
- Misleading or unclear
- Too long or too short
- Inappropriate tone
- Doesn't match content

### Text Review

**Approve if:**
- 400-800 words (flexible range)
- Appropriate B2 vocabulary level
- Well-structured paragraphs
- Culturally neutral content
- Engaging and authentic

**Reject if:**
- Wrong length (too short/long)
- Inappropriate language level
- Poor structure or flow
- Cultural bias or inappropriate content
- Factual errors

### Question Review

**Approve if:**
- Clear and unambiguous
- One obviously correct answer
- Appropriate difficulty level
- Tests intended skill (inference, detail, etc.)
- Realistic distractors

**Reject if:**
- Ambiguous or unclear
- Multiple correct answers
- Too easy or too difficult
- Doesn't test intended skill
- Poor distractors

## QA Summary and Reporting

### Completion Metrics

The system tracks:
- **Approved**: Number of approved elements
- **Rejected**: Number of rejected elements  
- **Pending**: Number of pending reviews
- **Completion Rate**: Percentage of elements reviewed

### QA History

View detailed review history including:
- Reviewer names and timestamps
- Status changes over time
- Detailed notes and feedback
- Review patterns and trends

## Best Practices

### For Reviewers

1. **Be Consistent**: Apply the same standards across all tasks
2. **Be Specific**: Provide detailed, actionable feedback
3. **Be Constructive**: Focus on improvement suggestions
4. **Be Thorough**: Review all elements carefully
5. **Document Issues**: Record specific problems clearly

### For Quality Control

1. **Regular Reviews**: Establish regular QA review cycles
2. **Multiple Reviewers**: Use multiple reviewers for important tasks
3. **Feedback Integration**: Use QA feedback to improve generation
4. **Standards Documentation**: Maintain clear quality standards
5. **Training**: Ensure reviewers understand B2 First requirements

## Troubleshooting

### Common Issues

**QA Interface Not Loading**
- Check that you've selected a valid task
- Ensure the task file is accessible
- Try refreshing the page

**Cannot Save Annotations**
- Verify reviewer name is entered
- Check file permissions
- Ensure task file path is valid

**Missing QA Data**
- QA annotations are initialized automatically
- Check JSON file structure
- Verify file encoding (UTF-8)

### Error Recovery

If QA data is corrupted:
1. Check the JSON file syntax
2. Restore from backup if available
3. Re-initialize QA annotations
4. Contact system administrator

## Integration with Workflow

### Quality Control Pipeline

1. **Generation**: AI generates initial task
2. **Automatic Validation**: System checks basic requirements
3. **QA Review**: Human reviewer evaluates quality
4. **Revision**: Address rejected elements
5. **Final Approval**: Complete QA process
6. **Publication**: Release approved tasks

### Reporting and Analytics

Use QA data for:
- Quality trend analysis
- Reviewer performance tracking
- Content improvement insights
- Standards compliance monitoring
- Training needs identification

## Future Enhancements

Planned improvements:
- Batch QA operations
- QA workflow automation
- Advanced reporting dashboards
- Integration with content management systems
- Machine learning quality prediction 