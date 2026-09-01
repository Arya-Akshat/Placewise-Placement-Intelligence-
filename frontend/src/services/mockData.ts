import { Message, ConversationSummary } from '../types';

export const MOCK_CONVERSATIONS: ConversationSummary[] = [
  {
    conversation_id: 'conv_mock_1',
    title: 'CSE 2024 Placement Analysis',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_message: 'CSE placement rate for 2024 was 51.49%.',
    message_count: 2
  },
  {
    conversation_id: 'conv_mock_2',
    title: 'Top Hiring Companies',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: new Date(Date.now() - 86400000).toISOString(),
    last_message: 'Top 10 recruiters ranked by hiring volume.',
    message_count: 4
  }
];

export function getMockResponse(prompt: string): Message {
  const p = prompt.toLowerCase();
  const now = new Date().toISOString();
  const id = `msg_mock_${Date.now()}`;

  if (p.includes('placement rate for cse')) {
    return {
      message_id: id,
      role: 'assistant',
      content: 'CSE placement rate for the 2024 graduating cohort was 51.49%, based on 1,159 placed students out of 2,251 eligible students with an average package of ₹8.92 LPA.',
      status: 'COMPLETED',
      created_at: now,
      attachment: {
        query_id: 'qry_mock_1',
        source_object: 'semantic.genie_department_performance',
        target_metric: 'placement_rate',
        recommended_visualization: 'KPI',
        kpis: [
          { label: 'Placement Rate', value: '51.49%' },
          { label: 'Placed Students', value: '1,159' },
          { label: 'Eligible Students', value: '2,251' },
          { label: 'Average CTC', value: '₹8.92 LPA' }
        ],
        table_data: {
          columns: [
            { name: 'department_code', type_text: 'STRING', display_name: 'Department' },
            { name: 'graduation_year', type_text: 'INT', display_name: 'Batch' },
            { name: 'total_students', type_text: 'BIGINT', display_name: 'Total' },
            { name: 'eligible_students', type_text: 'BIGINT', display_name: 'Eligible' },
            { name: 'placed_students', type_text: 'BIGINT', display_name: 'Placed' },
            { name: 'placement_rate', type_text: 'DOUBLE', display_name: 'Placement Rate' }
          ],
          rows: [
            { department_code: 'CSE', graduation_year: 2024, total_students: 2529, eligible_students: 2251, placed_students: 1159, placement_rate: 51.49 }
          ],
          total_row_count: 1,
          truncated: false
        }
      },
      follow_up_suggestions: [
        'How does that compare with ECE?',
        'Show placement rate across all departments',
        'Which companies hired the most CSE students?'
      ]
    };
  }

  return {
    message_id: id,
    role: 'assistant',
    content: 'Showing placement intelligence analytics from the governed Placewise semantic layer.',
    status: 'COMPLETED',
    created_at: now
  };
}
