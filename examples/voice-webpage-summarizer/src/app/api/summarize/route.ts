import { NextRequest, NextResponse } from 'next/server';
import { ACI } from '@aci-sdk/aci';

const client = new ACI({ apiKey: process.env.ACI_API_KEY || '' });

export async function POST(request: NextRequest) {
  try {
    const { url } = await request.json();

    if (!url) {
      return NextResponse.json({ success: false, error: 'URL is required' }, { status: 400 });
    }

    const functions = await client.functions.search({
      intent: "I want to extract content from a webpage",
      allowed_apps_only: false,
      limit: 10
    });

    const exaFunctions = await client.functions.search({
      intent: "I want to use EXA_AI for answering questions and summarization",
      allowed_apps_only: false,
      limit: 5
    });

    const allFunctions = [...functions, ...exaFunctions];
    const uniqueFunctions = allFunctions.filter((f, index, self) => 
      index === self.findIndex(ff => (ff as any).name === (f as any).name)
    );
    
    if (uniqueFunctions.length === 0) {
      return NextResponse.json({
        success: false,
        error: 'No functions found',
        suggestion: 'Configure Firecrawl, EXA_AI, and ElevenLabs in your ACI.dev account'
      }, { status: 500 });
    }

    const exaFunction = uniqueFunctions.find(f => (f as any).name === 'EXA_AI__ANSWER');

    if (!exaFunction) {
      return NextResponse.json({
        success: false,
        error: 'No EXA_AI function found',
        suggestion: 'Configure EXA_AI in your ACI.dev account'
      }, { status: 500 });
    }

    let summaryResult = null;
    try {
      summaryResult = await client.functions.execute({
        function_name: (exaFunction as any).name,
        function_parameters: {
          body: {
            query: `Analyze and summarize the content from this URL: ${url}. 

Please provide a comprehensive, well-organized summary in the following format:

## Overview
Brief description of what the webpage is about

## Key Points
- Main point 1
- Main point 2
- Main point 3

## Description
Detailed explanation of the content, purpose, and important information

## Summary
Concise conclusion of the main takeaways

Focus only on the main content of this specific webpage. Do not reference external sources, links, or citations. Provide your response in English only with clear structure and formatting.`
          }
        },
        linked_account_owner_id: 'demo_user'
      });

    } catch (summaryError) {
      summaryResult = {
        data: {
          answer: `Unable to extract detailed content from ${url}. This could be due to website protection, slow loading times, or other technical issues. Please try a different website or contact support if this persists.`
        }
      };
    }

    const summary = summaryResult.data?.answer || 'No summary available';

    // Send summary to Slack via ACI
    try {
      // Format the summary for better Slack display
      const formattedSummary = summary
        .replace(/## Overview\n/g, '*Overview*\n')
        .replace(/## Key Points\n/g, '*Key Points*\n')
        .replace(/## Description\n/g, '*Description*\n')
        .replace(/## Summary\n/g, '*Summary*\n')
        .replace(/^- /g, '• ');

      const slackMessage = `*New Summary Generated*\n\n*URL:* ${url}\n\n${formattedSummary}`;
      
      await client.functions.execute({
        function_name: 'SLACK__CHAT_POST_MESSAGE',
        function_parameters: {
          body: {
            text: slackMessage,
            channel: process.env.SLACK_CHANNEL_ID || 'general'
          }
        },
        linked_account_owner_id: 'demo_user'
      });
      
      console.log('✅ Summary sent to Slack via ACI');
    } catch (slackError) {
      console.error('❌ Error sending to Slack via ACI:', slackError);
      // Continue execution even if Slack fails
    }

    return NextResponse.json({
      success: true,
      summary: summary,
      functionUsed: {
        exa: 'EXA_AI__ANSWER'
      }
    });

  } catch (error) {
    return NextResponse.json({ success: false, error: error instanceof Error ? error.message : 'Unknown error occurred' }, { status: 500 });
  }
} 