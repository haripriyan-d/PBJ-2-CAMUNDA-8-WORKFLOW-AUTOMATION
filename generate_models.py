import os
import xml.etree.ElementTree as ET

BASE_DIR = r"C:\Users\harip\.gemini\antigravity\scratch\PBJ-2-CAMUNDA-8-WORKFLOW-AUTOMATION"

# ==============================================================================
# LAB 1: Loan Approval Automation BPMN & DMN
# ==============================================================================

LAB1_BPMN = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                  xmlns:zeebe="http://camunda.org/schema/zeebe/1.0"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  id="Definitions_LoanApproval"
                  targetNamespace="http://bpmn.io/schema/bpmn"
                  exporter="Camunda Modeler"
                  exporterVersion="5.28.0">

  <bpmn:collaboration id="Collaboration_LoanApproval">
    <bpmn:participant id="Participant_LoanSystem" name="Camunda 8 End-to-End Loan Approval Platform" processRef="Process_LoanApproval" />
  </bpmn:collaboration>

  <bpmn:process id="Process_LoanApproval" name="End-to-End Loan Approval Workflow" isExecutable="true">
    <bpmn:laneSet id="LaneSet_Loan">
      <bpmn:lane id="Lane_AutomatedServices" name="Automated Services &amp; Decision Engine">
        <bpmn:flowNodeRef>StartEvent_LoanApplied</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_ValidateApplicant</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Gateway_Validation</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_CreditAssessment</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_EvaluateLoanDmn</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Gateway_DmnOutcome</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_PrepareDisbursement</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_NotifyApproved</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>EndEvent_Approved</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_NotifyRejected</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>EndEvent_Rejected</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_SendValidationFailure</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>EndEvent_ValidationFailed</bpmn:flowNodeRef>
      </bpmn:lane>
      <bpmn:lane id="Lane_UnderwriterReview" name="Credit Underwriter (Tasklist Human Review)">
        <bpmn:flowNodeRef>Task_ManualUnderwriterReview</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Gateway_UnderwriterDecision</bpmn:flowNodeRef>
      </bpmn:lane>
    </bpmn:laneSet>

    <!-- Start Event -->
    <bpmn:startEvent id="StartEvent_LoanApplied" name="Loan Application Submitted">
      <bpmn:outgoing>Flow_Start_To_Validate</bpmn:outgoing>
    </bpmn:startEvent>

    <!-- Service Task 1: Spring Boot External Worker -->
    <bpmn:serviceTask id="Task_ValidateApplicant" name="Validate Applicant Information">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="applicant-validator" retries="3" />
        <zeebe:ioMapping>
          <zeebe:input source="=applicantId" target="applicantId" />
          <zeebe:input source="=applicantName" target="applicantName" />
          <zeebe:input source="=requestedAmount" target="requestedAmount" />
          <zeebe:input source="=monthlyIncome" target="monthlyIncome" />
          <zeebe:input source="=employmentYears" target="employmentYears" />
          <zeebe:output source="=isValid" target="isValid" />
          <zeebe:output source="=debtToIncomeRatio" target="debtToIncomeRatio" />
          <zeebe:output source="=validationMessage" target="validationMessage" />
        </zeebe:ioMapping>
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Start_To_Validate</bpmn:incoming>
      <bpmn:outgoing>Flow_Validate_To_Gateway</bpmn:outgoing>
    </bpmn:serviceTask>

    <!-- Exclusive Gateway: Validation Check -->
    <bpmn:exclusiveGateway id="Gateway_Validation" name="Applicant Data Valid?" default="Flow_Val_Valid">
      <bpmn:incoming>Flow_Validate_To_Gateway</bpmn:incoming>
      <bpmn:outgoing>Flow_Val_Valid</bpmn:outgoing>
      <bpmn:outgoing>Flow_Val_Invalid</bpmn:outgoing>
    </bpmn:exclusiveGateway>

    <!-- REST Outbound Connector: Camunda 8 HTTP JSON (io.camunda.connectors.HttpJson.v1) -->
    <bpmn:serviceTask id="Task_CreditAssessment" name="Call Credit Assessment REST API (REST Outbound Connector)"
                      zeebe:modelerTemplate="io.camunda.connectors.HttpJson.v1"
                      zeebe:modelerTemplateVersion="1"
                      zeebe:modelerTemplateIcon="data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2218%22%20height%3D%2218%22%20fill%3D%22none%22%20viewBox%3D%220%200%2018%2018%22%3E%3Cpath%20stroke%3D%22currentColor%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%20stroke-width%3D%222%22%20d%3D%22M2%209h14M11%204l5%205-5%205%22%2F%3E%3C%2Fsvg%3E">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="io.camunda:http-json:1" retries="3" />
        <zeebe:taskHeaders>
          <zeebe:header key="resultVariable" value="response" />
          <zeebe:header key="errorExpression" value="" />
          <zeebe:header key="resultExpression" value="" />
        </zeebe:taskHeaders>
        <zeebe:ioMapping>
          <zeebe:input source="http://localhost:8081/api/v1/credit-assessment" target="url" />
          <zeebe:input source="post" target="method" />
          <zeebe:input source="={applicantId: applicantId, requestedAmount: requestedAmount, monthlyIncome: monthlyIncome}" target="body" />
          <zeebe:input source="20" target="connectionTimeoutInSeconds" />
          <zeebe:input source="noAuth" target="authentication.type" />
          <zeebe:output source="=response.body.creditScore" target="creditScore" />
          <zeebe:output source="=response.body.creditTier" target="creditTier" />
          <zeebe:output source="=response.body.assessmentStatus" target="assessmentStatus" />
        </zeebe:ioMapping>
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Val_Valid</bpmn:incoming>
      <bpmn:outgoing>Flow_Credit_To_Dmn</bpmn:outgoing>
    </bpmn:serviceTask>

    <!-- Business Rule Task: Camunda 8 DMN -->
    <bpmn:businessRuleTask id="Task_EvaluateLoanDmn" name="Evaluate Loan Decision Rules (DMN)">
      <bpmn:extensionElements>
        <zeebe:calledDecision decisionId="Decision_LoanEligibility" resultVariable="dmnDecisionResult" />
        <zeebe:ioMapping>
          <zeebe:output source="=dmnDecisionResult.decision" target="dmnDecision" />
          <zeebe:output source="=dmnDecisionResult.reason" target="decisionReason" />
        </zeebe:ioMapping>
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Credit_To_Dmn</bpmn:incoming>
      <bpmn:outgoing>Flow_Dmn_To_Gateway</bpmn:outgoing>
    </bpmn:businessRuleTask>

    <!-- Exclusive Gateway: DMN Decision Outcome -->
    <bpmn:exclusiveGateway id="Gateway_DmnOutcome" name="DMN Decision Outcome" default="Flow_Dmn_Manual">
      <bpmn:incoming>Flow_Dmn_To_Gateway</bpmn:incoming>
      <bpmn:outgoing>Flow_Dmn_Approved</bpmn:outgoing>
      <bpmn:outgoing>Flow_Dmn_Rejected</bpmn:outgoing>
      <bpmn:outgoing>Flow_Dmn_Manual</bpmn:outgoing>
    </bpmn:exclusiveGateway>

    <!-- User Task: Manual Underwriter Review -->
    <bpmn:userTask id="Task_ManualUnderwriterReview" name="Manual Underwriter Review">
      <bpmn:extensionElements>
        <zeebe:formDefinition formId="Form_ManualLoanReview" />
        <zeebe:assignmentDefinition candidateGroups="loan-officers, underwriters" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Dmn_Manual</bpmn:incoming>
      <bpmn:outgoing>Flow_Review_To_Gateway</bpmn:outgoing>
    </bpmn:userTask>

    <!-- Exclusive Gateway: Underwriter Verdict -->
    <bpmn:exclusiveGateway id="Gateway_UnderwriterDecision" name="Underwriter Approval?" default="Flow_Underwriter_Reject">
      <bpmn:incoming>Flow_Review_To_Gateway</bpmn:incoming>
      <bpmn:outgoing>Flow_Underwriter_Approve</bpmn:outgoing>
      <bpmn:outgoing>Flow_Underwriter_Reject</bpmn:outgoing>
    </bpmn:exclusiveGateway>

    <!-- Automated Approval Path -->
    <bpmn:serviceTask id="Task_PrepareDisbursement" name="Prepare Disbursement &amp; Sanction Letter">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="loan-disbursement" retries="3" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Dmn_Approved</bpmn:incoming>
      <bpmn:incoming>Flow_Underwriter_Approve</bpmn:incoming>
      <bpmn:outgoing>Flow_Disburse_To_Notify</bpmn:outgoing>
    </bpmn:serviceTask>

    <bpmn:sendTask id="Task_NotifyApproved" name="Notify Applicant: Loan Approved">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="notification-service" retries="3" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Disburse_To_Notify</bpmn:incoming>
      <bpmn:outgoing>Flow_NotifyApprove_To_End</bpmn:outgoing>
    </bpmn:sendTask>

    <bpmn:endEvent id="EndEvent_Approved" name="Loan Sanctioned &amp; Disbursed">
      <bpmn:incoming>Flow_NotifyApprove_To_End</bpmn:incoming>
    </bpmn:endEvent>

    <!-- Rejection Path -->
    <bpmn:sendTask id="Task_NotifyRejected" name="Send Adverse Action Rejection Letter">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="notification-service" retries="3" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Dmn_Rejected</bpmn:incoming>
      <bpmn:incoming>Flow_Underwriter_Reject</bpmn:incoming>
      <bpmn:outgoing>Flow_NotifyReject_To_End</bpmn:outgoing>
    </bpmn:sendTask>

    <bpmn:endEvent id="EndEvent_Rejected" name="Loan Rejected">
      <bpmn:incoming>Flow_NotifyReject_To_End</bpmn:incoming>
    </bpmn:endEvent>

    <!-- Validation Failure Path -->
    <bpmn:sendTask id="Task_SendValidationFailure" name="Notify Invalid Application Details">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="notification-service" retries="3" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Val_Invalid</bpmn:incoming>
      <bpmn:outgoing>Flow_ValFail_To_End</bpmn:outgoing>
    </bpmn:sendTask>

    <bpmn:endEvent id="EndEvent_ValidationFailed" name="Rejected - Data Validation Error">
      <bpmn:incoming>Flow_ValFail_To_End</bpmn:incoming>
    </bpmn:endEvent>

    <!-- Sequence Flows -->
    <bpmn:sequenceFlow id="Flow_Start_To_Validate" sourceRef="StartEvent_LoanApplied" targetRef="Task_ValidateApplicant" />
    <bpmn:sequenceFlow id="Flow_Validate_To_Gateway" sourceRef="Task_ValidateApplicant" targetRef="Gateway_Validation" />
    <bpmn:sequenceFlow id="Flow_Val_Valid" name="Valid" sourceRef="Gateway_Validation" targetRef="Task_CreditAssessment" />
    <bpmn:sequenceFlow id="Flow_Val_Invalid" name="Invalid Data" sourceRef="Gateway_Validation" targetRef="Task_SendValidationFailure">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">=isValid = false</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="Flow_ValFail_To_End" sourceRef="Task_SendValidationFailure" targetRef="EndEvent_ValidationFailed" />
    <bpmn:sequenceFlow id="Flow_Credit_To_Dmn" sourceRef="Task_CreditAssessment" targetRef="Task_EvaluateLoanDmn" />
    <bpmn:sequenceFlow id="Flow_Dmn_To_Gateway" sourceRef="Task_EvaluateLoanDmn" targetRef="Gateway_DmnOutcome" />
    <bpmn:sequenceFlow id="Flow_Dmn_Approved" name="Approved" sourceRef="Gateway_DmnOutcome" targetRef="Task_PrepareDisbursement">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">=dmnDecision = "Approved"</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="Flow_Dmn_Rejected" name="Rejected" sourceRef="Gateway_DmnOutcome" targetRef="Task_NotifyRejected">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">=dmnDecision = "Rejected"</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="Flow_Dmn_Manual" name="Manual Review" sourceRef="Gateway_DmnOutcome" targetRef="Task_ManualUnderwriterReview" />
    <bpmn:sequenceFlow id="Flow_Review_To_Gateway" sourceRef="Task_ManualUnderwriterReview" targetRef="Gateway_UnderwriterDecision" />
    <bpmn:sequenceFlow id="Flow_Underwriter_Approve" name="Approve" sourceRef="Gateway_UnderwriterDecision" targetRef="Task_PrepareDisbursement">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">=reviewDecision = "Approved"</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="Flow_Underwriter_Reject" name="Reject" sourceRef="Gateway_UnderwriterDecision" targetRef="Task_NotifyRejected" />
    <bpmn:sequenceFlow id="Flow_Disburse_To_Notify" sourceRef="Task_PrepareDisbursement" targetRef="Task_NotifyApproved" />
    <bpmn:sequenceFlow id="Flow_NotifyApprove_To_End" sourceRef="Task_NotifyApproved" targetRef="EndEvent_Approved" />
    <bpmn:sequenceFlow id="Flow_NotifyReject_To_End" sourceRef="Task_NotifyRejected" targetRef="EndEvent_Rejected" />

  </bpmn:process>

  <!-- BPMNDI Layout Coordinates -->
  <bpmndi:BPMNDiagram id="BPMNDiagram_Loan">
    <bpmndi:BPMNPlane id="BPMNPlane_Loan" bpmnElement="Collaboration_LoanApproval">
      <bpmndi:BPMNShape id="Shape_Participant_LoanSystem" bpmnElement="Participant_LoanSystem" isHorizontal="true">
        <dc:Bounds x="160" y="80" width="1380" height="480" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Shape_Lane_AutomatedServices" bpmnElement="Lane_AutomatedServices" isHorizontal="true">
        <dc:Bounds x="190" y="80" width="1350" height="280" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Shape_Lane_UnderwriterReview" bpmnElement="Lane_UnderwriterReview" isHorizontal="true">
        <dc:Bounds x="190" y="360" width="1350" height="200" />
      </bpmndi:BPMNShape>

      <!-- Nodes -->
      <bpmndi:BPMNShape id="Shape_StartEvent_LoanApplied" bpmnElement="StartEvent_LoanApplied">
        <dc:Bounds x="232" y="162" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="210" y="205" width="81" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_ValidateApplicant" bpmnElement="Task_ValidateApplicant">
        <dc:Bounds x="320" y="140" width="120" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Gateway_Validation" bpmnElement="Gateway_Validation" isMarkerVisible="true">
        <dc:Bounds x="485" y="155" width="50" height="50" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="473" y="125" width="75" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_CreditAssessment" bpmnElement="Task_CreditAssessment">
        <dc:Bounds x="580" y="140" width="130" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_EvaluateLoanDmn" bpmnElement="Task_EvaluateLoanDmn">
        <dc:Bounds x="750" y="140" width="130" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Gateway_DmnOutcome" bpmnElement="Gateway_DmnOutcome" isMarkerVisible="true">
        <dc:Bounds x="925" y="155" width="50" height="50" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="912" y="125" width="76" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_PrepareDisbursement" bpmnElement="Task_PrepareDisbursement">
        <dc:Bounds x="1050" y="110" width="130" height="70" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_NotifyApproved" bpmnElement="Task_NotifyApproved">
        <dc:Bounds x="1220" y="110" width="120" height="70" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_EndEvent_Approved" bpmnElement="EndEvent_Approved">
        <dc:Bounds x="1382" y="127" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="1361" y="170" width="78" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_NotifyRejected" bpmnElement="Task_NotifyRejected">
        <dc:Bounds x="1050" y="210" width="130" height="70" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_EndEvent_Rejected" bpmnElement="EndEvent_Rejected">
        <dc:Bounds x="1232" y="227" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="1215" y="270" width="71" height="14" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_SendValidationFailure" bpmnElement="Task_SendValidationFailure">
        <dc:Bounds x="450" y="260" width="120" height="60" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_EndEvent_ValidationFailed" bpmnElement="EndEvent_ValidationFailed">
        <dc:Bounds x="612" y="272" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="591" y="315" width="79" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_ManualUnderwriterReview" bpmnElement="Task_ManualUnderwriterReview">
        <dc:Bounds x="885" y="420" width="130" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Gateway_UnderwriterDecision" bpmnElement="Gateway_UnderwriterDecision" isMarkerVisible="true">
        <dc:Bounds x="1065" y="435" width="50" height="50" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="1061" y="492" width="58" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <!-- Edges -->
      <bpmndi:BPMNEdge id="Edge_Flow_Start_To_Validate" bpmnElement="Flow_Start_To_Validate">
        <di:waypoint x="268" y="180" />
        <di:waypoint x="320" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Validate_To_Gateway" bpmnElement="Flow_Validate_To_Gateway">
        <di:waypoint x="440" y="180" />
        <di:waypoint x="485" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Val_Valid" bpmnElement="Flow_Val_Valid">
        <di:waypoint x="535" y="180" />
        <di:waypoint x="580" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Val_Invalid" bpmnElement="Flow_Val_Invalid">
        <di:waypoint x="510" y="205" />
        <di:waypoint x="510" y="260" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_ValFail_To_End" bpmnElement="Flow_ValFail_To_End">
        <di:waypoint x="570" y="290" />
        <di:waypoint x="612" y="290" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Credit_To_Dmn" bpmnElement="Flow_Credit_To_Dmn">
        <di:waypoint x="710" y="180" />
        <di:waypoint x="750" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Dmn_To_Gateway" bpmnElement="Flow_Dmn_To_Gateway">
        <di:waypoint x="880" y="180" />
        <di:waypoint x="925" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Dmn_Approved" bpmnElement="Flow_Dmn_Approved">
        <di:waypoint x="950" y="155" />
        <di:waypoint x="950" y="145" />
        <di:waypoint x="1050" y="145" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Dmn_Rejected" bpmnElement="Flow_Dmn_Rejected">
        <di:waypoint x="950" y="205" />
        <di:waypoint x="950" y="245" />
        <di:waypoint x="1050" y="245" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Dmn_Manual" bpmnElement="Flow_Dmn_Manual">
        <di:waypoint x="950" y="205" />
        <di:waypoint x="950" y="420" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Review_To_Gateway" bpmnElement="Flow_Review_To_Gateway">
        <di:waypoint x="1015" y="460" />
        <di:waypoint x="1065" y="460" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Underwriter_Approve" bpmnElement="Flow_Underwriter_Approve">
        <di:waypoint x="1115" y="460" />
        <di:waypoint x="1150" y="460" />
        <di:waypoint x="1150" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Underwriter_Reject" bpmnElement="Flow_Underwriter_Reject">
        <di:waypoint x="1090" y="435" />
        <di:waypoint x="1090" y="280" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Disburse_To_Notify" bpmnElement="Flow_Disburse_To_Notify">
        <di:waypoint x="1180" y="145" />
        <di:waypoint x="1220" y="145" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_NotifyApprove_To_End" bpmnElement="Flow_NotifyApprove_To_End">
        <di:waypoint x="1340" y="145" />
        <di:waypoint x="1382" y="145" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_NotifyReject_To_End" bpmnElement="Flow_NotifyReject_To_End">
        <di:waypoint x="1180" y="245" />
        <di:waypoint x="1232" y="245" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>
"""

LAB1_DMN = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/"
             xmlns:dmndi="https://www.omg.org/spec/DMN/20191111/DMNDI/"
             xmlns:dc="http://www.omg.org/spec/DMN/20180521/DC/"
             id="Definitions_LoanRules"
             name="Loan Approval Decision Rules"
             namespace="http://camunda.org/schema/1.0/dmn"
             exporter="Camunda Modeler"
             exporterVersion="5.28.0">

  <decision id="Decision_LoanEligibility" name="Loan Eligibility &amp; Risk Classification">
    <decisionTable id="DecisionTable_Loan" hitPolicy="FIRST">
      <input id="Input_CreditScore" label="Credit Score">
        <inputExpression id="InputExpr_CreditScore" typeRef="number">
          <text>creditScore</text>
        </inputExpression>
      </input>
      <input id="Input_DtiRatio" label="Debt to Income Ratio (%)">
        <inputExpression id="InputExpr_DtiRatio" typeRef="number">
          <text>debtToIncomeRatio</text>
        </inputExpression>
      </input>
      <input id="Input_MonthlyIncome" label="Monthly Income ($)">
        <inputExpression id="InputExpr_MonthlyIncome" typeRef="number">
          <text>monthlyIncome</text>
        </inputExpression>
      </input>
      <output id="Output_Decision" label="Classification Decision" name="decision" typeRef="string" />
      <output id="Output_Reason" label="Underwriting Reason" name="reason" typeRef="string" />

      <!-- Rule 1: High credit score, low DTI, sufficient income -> Approved -->
      <rule id="Rule_PrimeApproval">
        <inputEntry id="Entry_1_1"><text>&gt;= 740</text></inputEntry>
        <inputEntry id="Entry_1_2"><text>&lt;= 35</text></inputEntry>
        <inputEntry id="Entry_1_3"><text>&gt;= 3500</text></inputEntry>
        <outputEntry id="Out_1_1"><text>"Approved"</text></outputEntry>
        <outputEntry id="Out_1_2"><text>"Prime applicant: High credit score and healthy debt-to-income ratio"</text></outputEntry>
      </rule>

      <!-- Rule 2: Subprime credit score -> Rejected -->
      <rule id="Rule_LowCreditReject">
        <inputEntry id="Entry_2_1"><text>&lt; 600</text></inputEntry>
        <inputEntry id="Entry_2_2"><text>-</text></inputEntry>
        <inputEntry id="Entry_2_3"><text>-</text></inputEntry>
        <outputEntry id="Out_2_1"><text>"Rejected"</text></outputEntry>
        <outputEntry id="Out_2_2"><text>"Credit score below minimum lending threshold (600)"</text></outputEntry>
      </rule>

      <!-- Rule 3: Excessive DTI ratio -> Rejected -->
      <rule id="Rule_HighDtiReject">
        <inputEntry id="Entry_3_1"><text>-</text></inputEntry>
        <inputEntry id="Entry_3_2"><text>&gt; 50</text></inputEntry>
        <inputEntry id="Entry_3_3"><text>-</text></inputEntry>
        <outputEntry id="Out_3_1"><text>"Rejected"</text></outputEntry>
        <outputEntry id="Out_3_2"><text>"Debt-to-income ratio exceeds statutory maximum threshold (50%)"</text></outputEntry>
      </rule>

      <!-- Rule 4: Insufficient monthly income -> Rejected -->
      <rule id="Rule_LowIncomeReject">
        <inputEntry id="Entry_4_1"><text>-</text></inputEntry>
        <inputEntry id="Entry_4_2"><text>-</text></inputEntry>
        <inputEntry id="Entry_4_3"><text>&lt; 2000</text></inputEntry>
        <outputEntry id="Out_4_1"><text>"Rejected"</text></outputEntry>
        <outputEntry id="Out_4_2"><text>"Monthly verifiable income below minimum qualification bar ($2,000)"</text></outputEntry>
      </rule>

      <!-- Rule 5: Moderate credit and moderate DTI -> Manual Review -->
      <rule id="Rule_ModerateReview">
        <inputEntry id="Entry_5_1"><text>[600..739]</text></inputEntry>
        <inputEntry id="Entry_5_2"><text>&lt;= 45</text></inputEntry>
        <inputEntry id="Entry_5_3"><text>&gt;= 2500</text></inputEntry>
        <outputEntry id="Out_5_1"><text>"Manual Review"</text></outputEntry>
        <outputEntry id="Out_5_2"><text>"Borderline risk parameters require human underwriter discretionary assessment"</text></outputEntry>
      </rule>

      <!-- Rule 6: Fallthrough catch-all -> Manual Review -->
      <rule id="Rule_FallbackReview">
        <inputEntry id="Entry_6_1"><text>-</text></inputEntry>
        <inputEntry id="Entry_6_2"><text>-</text></inputEntry>
        <inputEntry id="Entry_6_3"><text>-</text></inputEntry>
        <outputEntry id="Out_6_1"><text>"Manual Review"</text></outputEntry>
        <outputEntry id="Out_6_2"><text>"Non-standard risk tier requires underwriter policy override"</text></outputEntry>
      </rule>
    </decisionTable>
  </decision>

  <dmndi:DMNDI>
    <dmndi:DMNDiagram id="DMNDiagram_Loan">
      <dmndi:DMNShape id="DMNShape_Decision_LoanEligibility" dmnElementRef="Decision_LoanEligibility">
        <dc:Bounds x="160" y="100" width="220" height="80" />
      </dmndi:DMNShape>
    </dmndi:DMNDiagram>
  </dmndi:DMNDI>
</definitions>
"""

# ==============================================================================
# LAB 2: E-Commerce Order Processing and Fulfilment BPMN & DMN
# ==============================================================================

LAB2_BPMN = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                  xmlns:zeebe="http://camunda.org/schema/zeebe/1.0"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  id="Definitions_EcommerceOrder"
                  targetNamespace="http://bpmn.io/schema/bpmn"
                  exporter="Camunda Modeler"
                  exporterVersion="5.28.0">

  <bpmn:collaboration id="Collaboration_OrderProcessing">
    <bpmn:participant id="Participant_OrderProcessing" name="Camunda 8 E-Commerce Order Processing &amp; Fulfilment" processRef="Process_OrderProcessing" />
  </bpmn:collaboration>

  <bpmn:process id="Process_OrderProcessing" name="E-Commerce Order Processing and Fulfilment" isExecutable="true">
    <bpmn:laneSet id="LaneSet_Order">
      <bpmn:lane id="Lane_AutomatedPipeline" name="Automated Order Services &amp; Payment Gateway">
        <bpmn:flowNodeRef>StartEvent_OrderReceived</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_ValidateAndCheckStock</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Gateway_StockAvailability</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_DetermineOrderPriority</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Gateway_HighValueCheck</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_ProcessPaymentGateway</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Gateway_PaymentOutcome</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_DispatchFulfilment</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>EndEvent_Fulfilled</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_NotifyPaymentDeclined</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>EndEvent_PaymentDeclined</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_NotifyOutOfStock</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>EndEvent_OutOfStock</bpmn:flowNodeRef>
      </bpmn:lane>
      <bpmn:lane id="Lane_OperationsReview" name="Order Operations &amp; Risk Review (Tasklist)">
        <bpmn:flowNodeRef>Task_ManualOrderVerification</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Gateway_VerificationDecision</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_NotifyVerificationCancelled</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>EndEvent_VerificationCancelled</bpmn:flowNodeRef>
      </bpmn:lane>
    </bpmn:laneSet>

    <!-- Start Event -->
    <bpmn:startEvent id="StartEvent_OrderReceived" name="Customer Order Placed">
      <bpmn:outgoing>Flow_Start_To_Stock</bpmn:outgoing>
    </bpmn:startEvent>

    <!-- Service Task 1: External Java/Spring Boot Worker -->
    <bpmn:serviceTask id="Task_ValidateAndCheckStock" name="Validate Order &amp; Check Inventory Stock">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="order-validator-inventory" retries="3" />
        <zeebe:ioMapping>
          <zeebe:input source="=orderId" target="orderId" />
          <zeebe:input source="=productId" target="productId" />
          <zeebe:input source="=quantity" target="quantity" />
          <zeebe:input source="=unitPrice" target="unitPrice" />
          <zeebe:output source="=stockAvailable" target="stockAvailable" />
          <zeebe:output source="=availableStock" target="availableStock" />
          <zeebe:output source="=orderTotal" target="orderTotal" />
          <zeebe:output source="=validationStatus" target="validationStatus" />
        </zeebe:ioMapping>
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Start_To_Stock</bpmn:incoming>
      <bpmn:outgoing>Flow_Stock_To_Gateway</bpmn:outgoing>
    </bpmn:serviceTask>

    <!-- Exclusive Gateway: Stock Availability -->
    <bpmn:exclusiveGateway id="Gateway_StockAvailability" name="Stock Available?" default="Flow_Stock_Yes">
      <bpmn:incoming>Flow_Stock_To_Gateway</bpmn:incoming>
      <bpmn:outgoing>Flow_Stock_Yes</bpmn:outgoing>
      <bpmn:outgoing>Flow_Stock_No</bpmn:outgoing>
    </bpmn:exclusiveGateway>

    <!-- Business Rule Task: Camunda 8 DMN -->
    <bpmn:businessRuleTask id="Task_DetermineOrderPriority" name="Determine Order Priority (DMN)">
      <bpmn:extensionElements>
        <zeebe:calledDecision decisionId="Decision_OrderPriority" resultVariable="priorityResult" />
        <zeebe:ioMapping>
          <zeebe:output source="=priorityResult.orderPriority" target="orderPriority" />
          <zeebe:output source="=priorityResult.priorityReason" target="priorityReason" />
        </zeebe:ioMapping>
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Stock_Yes</bpmn:incoming>
      <bpmn:outgoing>Flow_Priority_To_HighValueGateway</bpmn:outgoing>
    </bpmn:businessRuleTask>

    <!-- Exclusive Gateway: High-Value or Critical Exception Check -->
    <bpmn:exclusiveGateway id="Gateway_HighValueCheck" name="Requires Manual Verification?" default="Flow_Route_Payment_Direct">
      <bpmn:incoming>Flow_Priority_To_HighValueGateway</bpmn:incoming>
      <bpmn:outgoing>Flow_Route_Payment_Direct</bpmn:outgoing>
      <bpmn:outgoing>Flow_Route_Manual_Review</bpmn:outgoing>
    </bpmn:exclusiveGateway>

    <!-- Tasklist User Task: Manual Order Verification -->
    <bpmn:userTask id="Task_ManualOrderVerification" name="Manual High-Value Order Verification">
      <bpmn:extensionElements>
        <zeebe:formDefinition formId="Form_OrderVerification" />
        <zeebe:assignmentDefinition candidateGroups="order-operations, fraud-review" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Route_Manual_Review</bpmn:incoming>
      <bpmn:outgoing>Flow_Review_To_VerifGateway</bpmn:outgoing>
    </bpmn:userTask>

    <!-- Exclusive Gateway: Verification Decision -->
    <bpmn:exclusiveGateway id="Gateway_VerificationDecision" name="Verification Approved?" default="Flow_Verif_Reject">
      <bpmn:incoming>Flow_Review_To_VerifGateway</bpmn:incoming>
      <bpmn:outgoing>Flow_Verif_Approve</bpmn:outgoing>
      <bpmn:outgoing>Flow_Verif_Reject</bpmn:outgoing>
    </bpmn:exclusiveGateway>

    <!-- REST Outbound Connector: Camunda 8 HTTP JSON (io.camunda.connectors.HttpJson.v1) -->
    <bpmn:serviceTask id="Task_ProcessPaymentGateway" name="Invoke Payment Gateway (REST Outbound Connector)"
                      zeebe:modelerTemplate="io.camunda.connectors.HttpJson.v1"
                      zeebe:modelerTemplateVersion="1"
                      zeebe:modelerTemplateIcon="data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2218%22%20height%3D%2218%22%20fill%3D%22none%22%20viewBox%3D%220%200%2018%2018%22%3E%3Cpath%20stroke%3D%22currentColor%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%20stroke-width%3D%222%22%20d%3D%22M2%209h14M11%204l5%205-5%205%22%2F%3E%3C%2Fsvg%3E">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="io.camunda:http-json:1" retries="3" />
        <zeebe:taskHeaders>
          <zeebe:header key="resultVariable" value="response" />
          <zeebe:header key="errorExpression" value="" />
          <zeebe:header key="resultExpression" value="" />
        </zeebe:taskHeaders>
        <zeebe:ioMapping>
          <zeebe:input source="http://localhost:8081/api/v1/payments/process" target="url" />
          <zeebe:input source="post" target="method" />
          <zeebe:input source="={orderId: orderId, customerRef: customerRef, amount: orderTotal, paymentToken: paymentToken}" target="body" />
          <zeebe:input source="20" target="connectionTimeoutInSeconds" />
          <zeebe:input source="noAuth" target="authentication.type" />
          <zeebe:output source="=response.body.paymentStatus" target="paymentStatus" />
          <zeebe:output source="=response.body.transactionId" target="transactionId" />
          <zeebe:output source="=response.body.authCode" target="authCode" />
        </zeebe:ioMapping>
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Route_Payment_Direct</bpmn:incoming>
      <bpmn:incoming>Flow_Verif_Approve</bpmn:incoming>
      <bpmn:outgoing>Flow_Payment_To_Gateway</bpmn:outgoing>
    </bpmn:serviceTask>

    <!-- Exclusive Gateway: Payment Outcome -->
    <bpmn:exclusiveGateway id="Gateway_PaymentOutcome" name="Payment Status Successful?" default="Flow_Payment_Failed">
      <bpmn:incoming>Flow_Payment_To_Gateway</bpmn:incoming>
      <bpmn:outgoing>Flow_Payment_Success</bpmn:outgoing>
      <bpmn:outgoing>Flow_Payment_Failed</bpmn:outgoing>
    </bpmn:exclusiveGateway>

    <!-- Fulfilment Path -->
    <bpmn:serviceTask id="Task_DispatchFulfilment" name="Dispatch Order to Warehouse Fulfilment">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="fulfilment-dispatcher" retries="3" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Payment_Success</bpmn:incoming>
      <bpmn:outgoing>Flow_Dispatch_To_End</bpmn:outgoing>
    </bpmn:serviceTask>

    <bpmn:endEvent id="EndEvent_Fulfilled" name="Order Fulfilled &amp; Dispatched">
      <bpmn:incoming>Flow_Dispatch_To_End</bpmn:incoming>
    </bpmn:endEvent>

    <!-- Payment Decline Path -->
    <bpmn:sendTask id="Task_NotifyPaymentDeclined" name="Notify Customer Payment Declined">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="notification-service" retries="3" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Payment_Failed</bpmn:incoming>
      <bpmn:outgoing>Flow_PayFail_To_End</bpmn:outgoing>
    </bpmn:sendTask>

    <bpmn:endEvent id="EndEvent_PaymentDeclined" name="Order Cancelled - Payment Declined">
      <bpmn:incoming>Flow_PayFail_To_End</bpmn:incoming>
    </bpmn:endEvent>

    <!-- Out of Stock Path -->
    <bpmn:sendTask id="Task_NotifyOutOfStock" name="Notify Customer Stock Unavailable">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="notification-service" retries="3" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Stock_No</bpmn:incoming>
      <bpmn:outgoing>Flow_StockNo_To_End</bpmn:outgoing>
    </bpmn:sendTask>

    <bpmn:endEvent id="EndEvent_OutOfStock" name="Order Cancelled - Insufficient Stock">
      <bpmn:incoming>Flow_StockNo_To_End</bpmn:incoming>
    </bpmn:endEvent>

    <!-- Verification Cancelled Path -->
    <bpmn:sendTask id="Task_NotifyVerificationCancelled" name="Notify Customer Order Flagged &amp; Cancelled">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="notification-service" retries="3" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Verif_Reject</bpmn:incoming>
      <bpmn:outgoing>Flow_VerifCancel_To_End</bpmn:outgoing>
    </bpmn:sendTask>

    <bpmn:endEvent id="EndEvent_VerificationCancelled" name="Order Cancelled - Review Rejection">
      <bpmn:incoming>Flow_VerifCancel_To_End</bpmn:incoming>
    </bpmn:endEvent>

    <!-- Sequence Flows -->
    <bpmn:sequenceFlow id="Flow_Start_To_Stock" sourceRef="StartEvent_OrderReceived" targetRef="Task_ValidateAndCheckStock" />
    <bpmn:sequenceFlow id="Flow_Stock_To_Gateway" sourceRef="Task_ValidateAndCheckStock" targetRef="Gateway_StockAvailability" />
    <bpmn:sequenceFlow id="Flow_Stock_Yes" name="In Stock" sourceRef="Gateway_StockAvailability" targetRef="Task_DetermineOrderPriority" />
    <bpmn:sequenceFlow id="Flow_Stock_No" name="Out of Stock" sourceRef="Gateway_StockAvailability" targetRef="Task_NotifyOutOfStock">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">=stockAvailable = false</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="Flow_StockNo_To_End" sourceRef="Task_NotifyOutOfStock" targetRef="EndEvent_OutOfStock" />
    <bpmn:sequenceFlow id="Flow_Priority_To_HighValueGateway" sourceRef="Task_DetermineOrderPriority" targetRef="Gateway_HighValueCheck" />
    <bpmn:sequenceFlow id="Flow_Route_Payment_Direct" name="Standard Value" sourceRef="Gateway_HighValueCheck" targetRef="Task_ProcessPaymentGateway" />
    <bpmn:sequenceFlow id="Flow_Route_Manual_Review" name="High Value / Critical" sourceRef="Gateway_HighValueCheck" targetRef="Task_ManualOrderVerification">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">=orderTotal &gt;= 2000 or orderPriority = "Critical"</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="Flow_Review_To_VerifGateway" sourceRef="Task_ManualOrderVerification" targetRef="Gateway_VerificationDecision" />
    <bpmn:sequenceFlow id="Flow_Verif_Approve" name="Approve" sourceRef="Gateway_VerificationDecision" targetRef="Task_ProcessPaymentGateway">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">=verificationStatus = "Approved"</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="Flow_Verif_Reject" name="Reject" sourceRef="Gateway_VerificationDecision" targetRef="Task_NotifyVerificationCancelled" />
    <bpmn:sequenceFlow id="Flow_VerifCancel_To_End" sourceRef="Task_NotifyVerificationCancelled" targetRef="EndEvent_VerificationCancelled" />
    <bpmn:sequenceFlow id="Flow_Payment_To_Gateway" sourceRef="Task_ProcessPaymentGateway" targetRef="Gateway_PaymentOutcome" />
    <bpmn:sequenceFlow id="Flow_Payment_Success" name="Payment Success" sourceRef="Gateway_PaymentOutcome" targetRef="Task_DispatchFulfilment">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">=paymentStatus = "SUCCESS"</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="Flow_Payment_Failed" name="Declined" sourceRef="Gateway_PaymentOutcome" targetRef="Task_NotifyPaymentDeclined" />
    <bpmn:sequenceFlow id="Flow_PayFail_To_End" sourceRef="Task_NotifyPaymentDeclined" targetRef="EndEvent_PaymentDeclined" />
    <bpmn:sequenceFlow id="Flow_Dispatch_To_End" sourceRef="Task_DispatchFulfilment" targetRef="EndEvent_Fulfilled" />

  </bpmn:process>

  <!-- BPMNDI Layout Coordinates -->
  <bpmndi:BPMNDiagram id="BPMNDiagram_Order">
    <bpmndi:BPMNPlane id="BPMNPlane_Order" bpmnElement="Collaboration_OrderProcessing">
      <bpmndi:BPMNShape id="Shape_Participant_OrderProcessing" bpmnElement="Participant_OrderProcessing" isHorizontal="true">
        <dc:Bounds x="160" y="80" width="1440" height="490" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Shape_Lane_AutomatedPipeline" bpmnElement="Lane_AutomatedPipeline" isHorizontal="true">
        <dc:Bounds x="190" y="80" width="1410" height="280" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Shape_Lane_OperationsReview" bpmnElement="Lane_OperationsReview" isHorizontal="true">
        <dc:Bounds x="190" y="360" width="1410" height="210" />
      </bpmndi:BPMNShape>

      <!-- Nodes -->
      <bpmndi:BPMNShape id="Shape_StartEvent_OrderReceived" bpmnElement="StartEvent_OrderReceived">
        <dc:Bounds x="232" y="162" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="210" y="205" width="81" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_ValidateAndCheckStock" bpmnElement="Task_ValidateAndCheckStock">
        <dc:Bounds x="320" y="140" width="130" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Gateway_StockAvailability" bpmnElement="Gateway_StockAvailability" isMarkerVisible="true">
        <dc:Bounds x="495" y="155" width="50" height="50" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="480" y="125" width="81" height="14" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_DetermineOrderPriority" bpmnElement="Task_DetermineOrderPriority">
        <dc:Bounds x="590" y="140" width="130" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Gateway_HighValueCheck" bpmnElement="Gateway_HighValueCheck" isMarkerVisible="true">
        <dc:Bounds x="765" y="155" width="50" height="50" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="748" y="120" width="84" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_ManualOrderVerification" bpmnElement="Task_ManualOrderVerification">
        <dc:Bounds x="725" y="420" width="130" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Gateway_VerificationDecision" bpmnElement="Gateway_VerificationDecision" isMarkerVisible="true">
        <dc:Bounds x="905" y="435" width="50" height="50" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="901" y="492" width="58" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_NotifyVerificationCancelled" bpmnElement="Task_NotifyVerificationCancelled">
        <dc:Bounds x="1010" y="420" width="120" height="70" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_EndEvent_VerificationCancelled" bpmnElement="EndEvent_VerificationCancelled">
        <dc:Bounds x="1182" y="437" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="1160" y="480" width="81" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_ProcessPaymentGateway" bpmnElement="Task_ProcessPaymentGateway">
        <dc:Bounds x="900" y="140" width="130" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Gateway_PaymentOutcome" bpmnElement="Gateway_PaymentOutcome" isMarkerVisible="true">
        <dc:Bounds x="1075" y="155" width="50" height="50" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="1060" y="120" width="81" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_DispatchFulfilment" bpmnElement="Task_DispatchFulfilment">
        <dc:Bounds x="1180" y="110" width="130" height="70" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_EndEvent_Fulfilled" bpmnElement="EndEvent_Fulfilled">
        <dc:Bounds x="1362" y="127" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="1345" y="170" width="71" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_NotifyPaymentDeclined" bpmnElement="Task_NotifyPaymentDeclined">
        <dc:Bounds x="1180" y="210" width="130" height="70" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_EndEvent_PaymentDeclined" bpmnElement="EndEvent_PaymentDeclined">
        <dc:Bounds x="1362" y="227" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="1340" y="270" width="81" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_NotifyOutOfStock" bpmnElement="Task_NotifyOutOfStock">
        <dc:Bounds x="460" y="260" width="120" height="60" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_EndEvent_OutOfStock" bpmnElement="EndEvent_OutOfStock">
        <dc:Bounds x="632" y="272" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="611" y="315" width="79" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <!-- Edges -->
      <bpmndi:BPMNEdge id="Edge_Flow_Start_To_Stock" bpmnElement="Flow_Start_To_Stock">
        <di:waypoint x="268" y="180" />
        <di:waypoint x="320" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Stock_To_Gateway" bpmnElement="Flow_Stock_To_Gateway">
        <di:waypoint x="450" y="180" />
        <di:waypoint x="495" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Stock_Yes" bpmnElement="Flow_Stock_Yes">
        <di:waypoint x="545" y="180" />
        <di:waypoint x="590" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Stock_No" bpmnElement="Flow_Stock_No">
        <di:waypoint x="520" y="205" />
        <di:waypoint x="520" y="260" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_StockNo_To_End" bpmnElement="Flow_StockNo_To_End">
        <di:waypoint x="580" y="290" />
        <di:waypoint x="632" y="290" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Priority_To_HighValueGateway" bpmnElement="Flow_Priority_To_HighValueGateway">
        <di:waypoint x="720" y="180" />
        <di:waypoint x="765" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Route_Payment_Direct" bpmnElement="Flow_Route_Payment_Direct">
        <di:waypoint x="815" y="180" />
        <di:waypoint x="900" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Route_Manual_Review" bpmnElement="Flow_Route_Manual_Review">
        <di:waypoint x="790" y="205" />
        <di:waypoint x="790" y="420" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Review_To_VerifGateway" bpmnElement="Flow_Review_To_VerifGateway">
        <di:waypoint x="855" y="460" />
        <di:waypoint x="905" y="460" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Verif_Approve" bpmnElement="Flow_Verif_Approve">
        <di:waypoint x="930" y="435" />
        <di:waypoint x="930" y="328" />
        <di:waypoint x="930" y="220" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Verif_Reject" bpmnElement="Flow_Verif_Reject">
        <di:waypoint x="955" y="460" />
        <di:waypoint x="1010" y="460" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_VerifCancel_To_End" bpmnElement="Flow_VerifCancel_To_End">
        <di:waypoint x="1130" y="455" />
        <di:waypoint x="1182" y="455" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Payment_To_Gateway" bpmnElement="Flow_Payment_To_Gateway">
        <di:waypoint x="1030" y="180" />
        <di:waypoint x="1075" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Payment_Success" bpmnElement="Flow_Payment_Success">
        <di:waypoint x="1100" y="155" />
        <di:waypoint x="1100" y="145" />
        <di:waypoint x="1180" y="145" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Payment_Failed" bpmnElement="Flow_Payment_Failed">
        <di:waypoint x="1100" y="205" />
        <di:waypoint x="1100" y="245" />
        <di:waypoint x="1180" y="245" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_PayFail_To_End" bpmnElement="Flow_PayFail_To_End">
        <di:waypoint x="1310" y="245" />
        <di:waypoint x="1362" y="245" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Dispatch_To_End" bpmnElement="Flow_Dispatch_To_End">
        <di:waypoint x="1310" y="145" />
        <di:waypoint x="1362" y="145" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>
"""

LAB2_DMN = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/"
             xmlns:dmndi="https://www.omg.org/spec/DMN/20191111/DMNDI/"
             xmlns:dc="http://www.omg.org/spec/DMN/20180521/DC/"
             id="Definitions_OrderPriorityRules"
             name="Order Priority Decision Rules"
             namespace="http://camunda.org/schema/1.0/dmn"
             exporter="Camunda Modeler"
             exporterVersion="5.28.0">

  <decision id="Decision_OrderPriority" name="Order Fulfilment Priority Determination">
    <decisionTable id="DecisionTable_Priority" hitPolicy="FIRST">
      <input id="Input_OrderValue" label="Order Value ($)">
        <inputExpression id="InputExpr_OrderValue" typeRef="number">
          <text>orderTotal</text>
        </inputExpression>
      </input>
      <input id="Input_CustomerCategory" label="Customer Category">
        <inputExpression id="InputExpr_CustomerCategory" typeRef="string">
          <text>customerCategory</text>
        </inputExpression>
      </input>
      <input id="Input_DeliveryPreference" label="Delivery Preference">
        <inputExpression id="InputExpr_DeliveryPreference" typeRef="string">
          <text>deliveryPreference</text>
        </inputExpression>
      </input>
      <output id="Output_OrderPriority" label="Order Priority" name="orderPriority" typeRef="string" />
      <output id="Output_PriorityReason" label="Classification Reason" name="priorityReason" typeRef="string" />

      <!-- Rule 1: VIP with Overnight Delivery -> Critical -->
      <rule id="Rule_VipOvernight">
        <inputEntry id="Entry_P1_1"><text>-</text></inputEntry>
        <inputEntry id="Entry_P1_2"><text>"VIP"</text></inputEntry>
        <inputEntry id="Entry_P1_3"><text>"OVERNIGHT"</text></inputEntry>
        <outputEntry id="Out_P1_1"><text>"Critical"</text></outputEntry>
        <outputEntry id="Out_P1_2"><text>"VIP customer with guaranteed overnight delivery SLA"</text></outputEntry>
      </rule>

      <!-- Rule 2: High Value Order (>= 2000) -> High -->
      <rule id="Rule_HighValue">
        <inputEntry id="Entry_P2_1"><text>&gt;= 2000</text></inputEntry>
        <inputEntry id="Entry_P2_2"><text>-</text></inputEntry>
        <inputEntry id="Entry_P2_3"><text>-</text></inputEntry>
        <outputEntry id="Out_P2_1"><text>"High"</text></outputEntry>
        <outputEntry id="Out_P2_2"><text>"High-value order exceeding enterprise priority threshold"</text></outputEntry>
      </rule>

      <!-- Rule 3: VIP Customer with any other delivery -> High -->
      <rule id="Rule_VipStandard">
        <inputEntry id="Entry_P3_1"><text>-</text></inputEntry>
        <inputEntry id="Entry_P3_2"><text>"VIP"</text></inputEntry>
        <inputEntry id="Entry_P3_3"><text>-</text></inputEntry>
        <outputEntry id="Out_P3_1"><text>"High"</text></outputEntry>
        <outputEntry id="Out_P3_2"><text>"VIP tier loyalty preference"</text></outputEntry>
      </rule>

      <!-- Rule 4: Regular Customer with Express/Overnight -> Medium -->
      <rule id="Rule_RegularExpress">
        <inputEntry id="Entry_P4_1"><text>-</text></inputEntry>
        <inputEntry id="Entry_P4_2"><text>"REGULAR"</text></inputEntry>
        <inputEntry id="Entry_P4_3"><text>"EXPRESS", "OVERNIGHT"</text></inputEntry>
        <outputEntry id="Out_P4_1"><text>"Medium"</text></outputEntry>
        <outputEntry id="Out_P4_2"><text>"Paid expedited shipping tier"</text></outputEntry>
      </rule>

      <!-- Rule 5: Fallthrough Catch-all -> Standard -->
      <rule id="Rule_StandardCatchall">
        <inputEntry id="Entry_P5_1"><text>-</text></inputEntry>
        <inputEntry id="Entry_P5_2"><text>-</text></inputEntry>
        <inputEntry id="Entry_P5_3"><text>-</text></inputEntry>
        <outputEntry id="Out_P5_1"><text>"Standard"</text></outputEntry>
        <outputEntry id="Out_P5_2"><text>"Standard fulfillment queue"</text></outputEntry>
      </rule>
    </decisionTable>
  </decision>

  <dmndi:DMNDI>
    <dmndi:DMNDiagram id="DMNDiagram_Priority">
      <dmndi:DMNShape id="DMNShape_Decision_OrderPriority" dmnElementRef="Decision_OrderPriority">
        <dc:Bounds x="160" y="100" width="220" height="80" />
      </dmndi:DMNShape>
    </dmndi:DMNDiagram>
  </dmndi:DMNDI>
</definitions>
"""

# ==============================================================================
# LAB 3: Hospital Appointment and Patient Triage BPMN & DMN
# ==============================================================================

LAB3_BPMN = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                  xmlns:zeebe="http://camunda.org/schema/zeebe/1.0"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  id="Definitions_HospitalTriage"
                  targetNamespace="http://bpmn.io/schema/bpmn"
                  exporter="Camunda Modeler"
                  exporterVersion="5.28.0">

  <bpmn:collaboration id="Collaboration_HospitalAppointment">
    <bpmn:participant id="Participant_HospitalPlatform" name="Camunda 8 Hospital Appointment &amp; Patient Triage Platform" processRef="Process_HospitalTriage" />
  </bpmn:collaboration>

  <bpmn:process id="Process_HospitalTriage" name="Hospital Appointment and Patient Triage Management" isExecutable="true">
    <bpmn:laneSet id="LaneSet_Hospital">
      <bpmn:lane id="Lane_AutomatedTriage" name="Automated Registration, Triage &amp; Scheduling Engine">
        <bpmn:flowNodeRef>StartEvent_AppointmentRequested</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_ValidatePatientRegistration</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Gateway_RegistrationValid</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_EvaluatePatientTriageDmn</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Gateway_TriageBranch</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_QueryAvailableSlotsRest</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Gateway_SlotAvailability</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_AutoBookAppointment</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_SendAppointmentConfirmation</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>EndEvent_AppointmentConfirmed</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_NotifyInvalidRegistration</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>EndEvent_RegistrationRejected</bpmn:flowNodeRef>
      </bpmn:lane>
      <bpmn:lane id="Lane_ClinicalStaff" name="Authorised Clinical Staff &amp; Emergency Team (Tasklist)">
        <bpmn:flowNodeRef>Task_ImmediateHumanAssessment</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>EndEvent_EmergencyCareAdmitted</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_PriorityStaffReview</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_StaffSlotOverrideReview</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>EndEvent_Waitlisted</bpmn:flowNodeRef>
      </bpmn:lane>
    </bpmn:laneSet>

    <!-- Start Event -->
    <bpmn:startEvent id="StartEvent_AppointmentRequested" name="Appointment Request Submitted">
      <bpmn:outgoing>Flow_Start_To_ValidateReg</bpmn:outgoing>
    </bpmn:startEvent>

    <!-- Service Task 1: External Java Worker -->
    <bpmn:serviceTask id="Task_ValidatePatientRegistration" name="Validate Registration &amp; Symptoms Payload">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="patient-registration-validator" retries="3" />
        <zeebe:ioMapping>
          <zeebe:input source="=patientId" target="patientId" />
          <zeebe:input source="=patientName" target="patientName" />
          <zeebe:input source="=symptomsSummary" target="symptomsSummary" />
          <zeebe:input source="=urgencyScore" target="urgencyScore" />
          <zeebe:output source="=registrationValid" target="registrationValid" />
          <zeebe:output source="=validationNotes" target="validationNotes" />
        </zeebe:ioMapping>
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Start_To_ValidateReg</bpmn:incoming>
      <bpmn:outgoing>Flow_ValidateReg_To_Gateway</bpmn:outgoing>
    </bpmn:serviceTask>

    <!-- Exclusive Gateway: Registration Validity -->
    <bpmn:exclusiveGateway id="Gateway_RegistrationValid" name="Registration Valid?" default="Flow_Reg_Valid">
      <bpmn:incoming>Flow_ValidateReg_To_Gateway</bpmn:incoming>
      <bpmn:outgoing>Flow_Reg_Valid</bpmn:outgoing>
      <bpmn:outgoing>Flow_Reg_Invalid</bpmn:outgoing>
    </bpmn:exclusiveGateway>

    <!-- Business Rule Task: Camunda 8 DMN -->
    <bpmn:businessRuleTask id="Task_EvaluatePatientTriageDmn" name="Evaluate Predefined Clinical Triage (DMN)">
      <bpmn:extensionElements>
        <zeebe:calledDecision decisionId="Decision_PatientTriage" resultVariable="triageOutcome" />
        <zeebe:ioMapping>
          <zeebe:output source="=triageOutcome.triageCategory" target="triageCategory" />
          <zeebe:output source="=triageOutcome.targetResponseMinutes" target="targetResponseMinutes" />
          <zeebe:output source="=triageOutcome.clinicalProtocol" target="clinicalProtocol" />
        </zeebe:ioMapping>
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Reg_Valid</bpmn:incoming>
      <bpmn:outgoing>Flow_TriageDmn_To_Gateway</bpmn:outgoing>
    </bpmn:businessRuleTask>

    <!-- Exclusive Gateway: Triage Category Routing -->
    <bpmn:exclusiveGateway id="Gateway_TriageBranch" name="Triage Classification?" default="Flow_Branch_Standard">
      <bpmn:incoming>Flow_TriageDmn_To_Gateway</bpmn:incoming>
      <bpmn:outgoing>Flow_Branch_Urgent</bpmn:outgoing>
      <bpmn:outgoing>Flow_Branch_Standard</bpmn:outgoing>
    </bpmn:exclusiveGateway>

    <!-- Tasklist User Task: Immediate Human Assessment for Urgent Cases -->
    <bpmn:userTask id="Task_ImmediateHumanAssessment" name="Immediate Emergency Human Assessment">
      <bpmn:extensionElements>
        <zeebe:formDefinition formId="Form_UrgentTriage" />
        <zeebe:assignmentDefinition candidateGroups="emergency-physicians, trauma-nurses" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Branch_Urgent</bpmn:incoming>
      <bpmn:outgoing>Flow_Urgent_To_Admitted</bpmn:outgoing>
    </bpmn:userTask>

    <bpmn:endEvent id="EndEvent_EmergencyCareAdmitted" name="Admitted for Immediate Clinical Intervention">
      <bpmn:incoming>Flow_Urgent_To_Admitted</bpmn:incoming>
    </bpmn:endEvent>

    <!-- REST Outbound Connector: Camunda 8 HTTP JSON (io.camunda.connectors.HttpJson.v1) -->
    <bpmn:serviceTask id="Task_QueryAvailableSlotsRest" name="Retrieve Available Slots (REST Outbound Connector)"
                      zeebe:modelerTemplate="io.camunda.connectors.HttpJson.v1"
                      zeebe:modelerTemplateVersion="1"
                      zeebe:modelerTemplateIcon="data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2218%22%20height%3D%2218%22%20fill%3D%22none%22%20viewBox%3D%220%200%2018%2018%22%3E%3Cpath%20stroke%3D%22currentColor%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%20stroke-width%3D%222%22%20d%3D%22M2%209h14M11%204l5%205-5%205%22%2F%3E%3C%2Fsvg%3E">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="io.camunda:http-json:1" retries="3" />
        <zeebe:taskHeaders>
          <zeebe:header key="resultVariable" value="response" />
          <zeebe:header key="errorExpression" value="" />
          <zeebe:header key="resultExpression" value="" />
        </zeebe:taskHeaders>
        <zeebe:ioMapping>
          <zeebe:input source="http://localhost:8081/api/v1/scheduling/available-slots" target="url" />
          <zeebe:input source="post" target="method" />
          <zeebe:input source="={patientId: patientId, appointmentPreference: appointmentPreference, triageCategory: triageCategory}" target="body" />
          <zeebe:input source="20" target="connectionTimeoutInSeconds" />
          <zeebe:input source="noAuth" target="authentication.type" />
          <zeebe:output source="=response.body.slotsAvailable" target="slotsAvailable" />
          <zeebe:output source="=response.body.slotCount" target="slotCount" />
          <zeebe:output source="=response.body.availableSlots" target="availableSlots" />
          <zeebe:output source="=response.body.recommendedDoctor" target="recommendedDoctor" />
        </zeebe:ioMapping>
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Branch_Standard</bpmn:incoming>
      <bpmn:outgoing>Flow_Scheduling_To_Gateway</bpmn:outgoing>
    </bpmn:serviceTask>

    <!-- Exclusive Gateway: Slot Availability & Priority Check -->
    <bpmn:exclusiveGateway id="Gateway_SlotAvailability" name="Evaluate Slots &amp; Triage" default="Flow_Slot_AutoBook">
      <bpmn:incoming>Flow_Scheduling_To_Gateway</bpmn:incoming>
      <bpmn:outgoing>Flow_Slot_None</bpmn:outgoing>
      <bpmn:outgoing>Flow_Slot_PriorityReview</bpmn:outgoing>
      <bpmn:outgoing>Flow_Slot_AutoBook</bpmn:outgoing>
    </bpmn:exclusiveGateway>

    <!-- Tasklist User Task: Priority Staff Review -->
    <bpmn:userTask id="Task_PriorityStaffReview" name="Priority Staff Clinical Scheduling Review">
      <bpmn:extensionElements>
        <zeebe:formDefinition formId="Form_PriorityStaffReview" />
        <zeebe:assignmentDefinition candidateGroups="triage-nurses, clinical-scheduling" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Slot_PriorityReview</bpmn:incoming>
      <bpmn:outgoing>Flow_PriorityReview_To_Confirm</bpmn:outgoing>
    </bpmn:userTask>

    <!-- Tasklist User Task: No Slots Available - Staff Slot Override -->
    <bpmn:userTask id="Task_StaffSlotOverrideReview" name="Authorised Staff Review: Slot Override &amp; Waitlist">
      <bpmn:extensionElements>
        <zeebe:formDefinition formId="Form_WaitlistOverride" />
        <zeebe:assignmentDefinition candidateGroups="clinical-scheduling" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Slot_None</bpmn:incoming>
      <bpmn:outgoing>Flow_Override_To_Waitlist</bpmn:outgoing>
    </bpmn:userTask>

    <bpmn:endEvent id="EndEvent_Waitlisted" name="Patient Placed on Expedited Waitlist">
      <bpmn:incoming>Flow_Override_To_Waitlist</bpmn:incoming>
    </bpmn:endEvent>

    <!-- Automated Booking Path -->
    <bpmn:serviceTask id="Task_AutoBookAppointment" name="Execute Automated Slot Booking">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="appointment-booking-worker" retries="3" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Slot_AutoBook</bpmn:incoming>
      <bpmn:outgoing>Flow_AutoBook_To_Confirm</bpmn:outgoing>
    </bpmn:serviceTask>

    <bpmn:sendTask id="Task_SendAppointmentConfirmation" name="Send Appointment Confirmation">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="notification-service" retries="3" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_AutoBook_To_Confirm</bpmn:incoming>
      <bpmn:incoming>Flow_PriorityReview_To_Confirm</bpmn:incoming>
      <bpmn:outgoing>Flow_Confirm_To_End</bpmn:outgoing>
    </bpmn:sendTask>

    <bpmn:endEvent id="EndEvent_AppointmentConfirmed" name="Appointment Confirmed &amp; Scheduled">
      <bpmn:incoming>Flow_Confirm_To_End</bpmn:incoming>
    </bpmn:endEvent>

    <!-- Invalid Registration Path -->
    <bpmn:sendTask id="Task_NotifyInvalidRegistration" name="Notify Registration Correction Needed">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="notification-service" retries="3" />
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_Reg_Invalid</bpmn:incoming>
      <bpmn:outgoing>Flow_RegFail_To_End</bpmn:outgoing>
    </bpmn:sendTask>

    <bpmn:endEvent id="EndEvent_RegistrationRejected" name="Registration Terminated">
      <bpmn:incoming>Flow_RegFail_To_End</bpmn:incoming>
    </bpmn:endEvent>

    <!-- Sequence Flows -->
    <bpmn:sequenceFlow id="Flow_Start_To_ValidateReg" sourceRef="StartEvent_AppointmentRequested" targetRef="Task_ValidatePatientRegistration" />
    <bpmn:sequenceFlow id="Flow_ValidateReg_To_Gateway" sourceRef="Task_ValidatePatientRegistration" targetRef="Gateway_RegistrationValid" />
    <bpmn:sequenceFlow id="Flow_Reg_Valid" name="Valid" sourceRef="Gateway_RegistrationValid" targetRef="Task_EvaluatePatientTriageDmn" />
    <bpmn:sequenceFlow id="Flow_Reg_Invalid" name="Invalid Details" sourceRef="Gateway_RegistrationValid" targetRef="Task_NotifyInvalidRegistration">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">=registrationValid = false</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="Flow_RegFail_To_End" sourceRef="Task_NotifyInvalidRegistration" targetRef="EndEvent_RegistrationRejected" />
    <bpmn:sequenceFlow id="Flow_TriageDmn_To_Gateway" sourceRef="Task_EvaluatePatientTriageDmn" targetRef="Gateway_TriageBranch" />
    <bpmn:sequenceFlow id="Flow_Branch_Urgent" name="Urgent Assessment" sourceRef="Gateway_TriageBranch" targetRef="Task_ImmediateHumanAssessment">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">=triageCategory = "Urgent Assessment"</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="Flow_Urgent_To_Admitted" sourceRef="Task_ImmediateHumanAssessment" targetRef="EndEvent_EmergencyCareAdmitted" />
    <bpmn:sequenceFlow id="Flow_Branch_Standard" name="Routine / Priority" sourceRef="Gateway_TriageBranch" targetRef="Task_QueryAvailableSlotsRest" />
    <bpmn:sequenceFlow id="Flow_Scheduling_To_Gateway" sourceRef="Task_QueryAvailableSlotsRest" targetRef="Gateway_SlotAvailability" />
    <bpmn:sequenceFlow id="Flow_Slot_None" name="No Slots Available" sourceRef="Gateway_SlotAvailability" targetRef="Task_StaffSlotOverrideReview">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">=slotsAvailable = false or slotCount = 0</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="Flow_Override_To_Waitlist" sourceRef="Task_StaffSlotOverrideReview" targetRef="EndEvent_Waitlisted" />
    <bpmn:sequenceFlow id="Flow_Slot_PriorityReview" name="Priority Review" sourceRef="Gateway_SlotAvailability" targetRef="Task_PriorityStaffReview">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">=triageCategory = "Priority Review"</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="Flow_PriorityReview_To_Confirm" sourceRef="Task_PriorityStaffReview" targetRef="Task_SendAppointmentConfirmation" />
    <bpmn:sequenceFlow id="Flow_Slot_AutoBook" name="Routine Available" sourceRef="Gateway_SlotAvailability" targetRef="Task_AutoBookAppointment" />
    <bpmn:sequenceFlow id="Flow_AutoBook_To_Confirm" sourceRef="Task_AutoBookAppointment" targetRef="Task_SendAppointmentConfirmation" />
    <bpmn:sequenceFlow id="Flow_Confirm_To_End" sourceRef="Task_SendAppointmentConfirmation" targetRef="EndEvent_AppointmentConfirmed" />

  </bpmn:process>

  <!-- BPMNDI Layout Coordinates -->
  <bpmndi:BPMNDiagram id="BPMNDiagram_Hospital">
    <bpmndi:BPMNPlane id="BPMNPlane_Hospital" bpmnElement="Collaboration_HospitalAppointment">
      <bpmndi:BPMNShape id="Shape_Participant_HospitalPlatform" bpmnElement="Participant_HospitalPlatform" isHorizontal="true">
        <dc:Bounds x="160" y="80" width="1440" height="490" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Shape_Lane_AutomatedTriage" bpmnElement="Lane_AutomatedTriage" isHorizontal="true">
        <dc:Bounds x="190" y="80" width="1410" height="280" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Shape_Lane_ClinicalStaff" bpmnElement="Lane_ClinicalStaff" isHorizontal="true">
        <dc:Bounds x="190" y="360" width="1410" height="210" />
      </bpmndi:BPMNShape>

      <!-- Nodes -->
      <bpmndi:BPMNShape id="Shape_StartEvent_AppointmentRequested" bpmnElement="StartEvent_AppointmentRequested">
        <dc:Bounds x="232" y="162" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="210" y="205" width="81" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_ValidatePatientRegistration" bpmnElement="Task_ValidatePatientRegistration">
        <dc:Bounds x="320" y="140" width="130" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Gateway_RegistrationValid" bpmnElement="Gateway_RegistrationValid" isMarkerVisible="true">
        <dc:Bounds x="495" y="155" width="50" height="50" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="480" y="125" width="81" height="14" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_EvaluatePatientTriageDmn" bpmnElement="Task_EvaluatePatientTriageDmn">
        <dc:Bounds x="590" y="140" width="130" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Gateway_TriageBranch" bpmnElement="Gateway_TriageBranch" isMarkerVisible="true">
        <dc:Bounds x="765" y="155" width="50" height="50" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="750" y="125" width="81" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_ImmediateHumanAssessment" bpmnElement="Task_ImmediateHumanAssessment">
        <dc:Bounds x="725" y="420" width="130" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_EndEvent_EmergencyCareAdmitted" bpmnElement="EndEvent_EmergencyCareAdmitted">
        <dc:Bounds x="902" y="442" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="878" y="485" width="84" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_QueryAvailableSlotsRest" bpmnElement="Task_QueryAvailableSlotsRest">
        <dc:Bounds x="870" y="140" width="140" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Gateway_SlotAvailability" bpmnElement="Gateway_SlotAvailability" isMarkerVisible="true">
        <dc:Bounds x="1055" y="155" width="50" height="50" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="1040" y="125" width="81" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_PriorityStaffReview" bpmnElement="Task_PriorityStaffReview">
        <dc:Bounds x="1015" y="420" width="130" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_StaffSlotOverrideReview" bpmnElement="Task_StaffSlotOverrideReview">
        <dc:Bounds x="1175" y="420" width="130" height="80" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_EndEvent_Waitlisted" bpmnElement="EndEvent_Waitlisted">
        <dc:Bounds x="1352" y="442" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="1330" y="485" width="81" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_AutoBookAppointment" bpmnElement="Task_AutoBookAppointment">
        <dc:Bounds x="1160" y="140" width="120" height="70" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_SendAppointmentConfirmation" bpmnElement="Task_SendAppointmentConfirmation">
        <dc:Bounds x="1320" y="140" width="120" height="70" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_EndEvent_AppointmentConfirmed" bpmnElement="EndEvent_AppointmentConfirmed">
        <dc:Bounds x="1482" y="157" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="1460" y="200" width="81" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_Task_NotifyInvalidRegistration" bpmnElement="Task_NotifyInvalidRegistration">
        <dc:Bounds x="460" y="260" width="120" height="60" />
      </bpmndi:BPMNShape>

      <bpmndi:BPMNShape id="Shape_EndEvent_RegistrationRejected" bpmnElement="EndEvent_RegistrationRejected">
        <dc:Bounds x="632" y="272" width="36" height="36" />
        <bpmndi:BPMNLabel>
          <dc:Bounds x="611" y="315" width="79" height="27" />
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>

      <!-- Edges -->
      <bpmndi:BPMNEdge id="Edge_Flow_Start_To_ValidateReg" bpmnElement="Flow_Start_To_ValidateReg">
        <di:waypoint x="268" y="180" />
        <di:waypoint x="320" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_ValidateReg_To_Gateway" bpmnElement="Flow_ValidateReg_To_Gateway">
        <di:waypoint x="450" y="180" />
        <di:waypoint x="495" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Reg_Valid" bpmnElement="Flow_Reg_Valid">
        <di:waypoint x="545" y="180" />
        <di:waypoint x="590" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Reg_Invalid" bpmnElement="Flow_Reg_Invalid">
        <di:waypoint x="520" y="205" />
        <di:waypoint x="520" y="260" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_RegFail_To_End" bpmnElement="Flow_RegFail_To_End">
        <di:waypoint x="580" y="290" />
        <di:waypoint x="632" y="290" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_TriageDmn_To_Gateway" bpmnElement="Flow_TriageDmn_To_Gateway">
        <di:waypoint x="720" y="180" />
        <di:waypoint x="765" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Branch_Urgent" bpmnElement="Flow_Branch_Urgent">
        <di:waypoint x="790" y="205" />
        <di:waypoint x="790" y="420" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Urgent_To_Admitted" bpmnElement="Flow_Urgent_To_Admitted">
        <di:waypoint x="855" y="460" />
        <di:waypoint x="902" y="460" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Branch_Standard" bpmnElement="Flow_Branch_Standard">
        <di:waypoint x="815" y="180" />
        <di:waypoint x="870" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Scheduling_To_Gateway" bpmnElement="Flow_Scheduling_To_Gateway">
        <di:waypoint x="1010" y="180" />
        <di:waypoint x="1055" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Slot_None" bpmnElement="Flow_Slot_None">
        <di:waypoint x="1080" y="205" />
        <di:waypoint x="1080" y="380" />
        <di:waypoint x="1240" y="380" />
        <di:waypoint x="1240" y="420" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Override_To_Waitlist" bpmnElement="Flow_Override_To_Waitlist">
        <di:waypoint x="1305" y="460" />
        <di:waypoint x="1352" y="460" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Slot_PriorityReview" bpmnElement="Flow_Slot_PriorityReview">
        <di:waypoint x="1080" y="205" />
        <di:waypoint x="1080" y="420" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_PriorityReview_To_Confirm" bpmnElement="Flow_PriorityReview_To_Confirm">
        <di:waypoint x="1145" y="460" />
        <di:waypoint x="1380" y="460" />
        <di:waypoint x="1380" y="210" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Slot_AutoBook" bpmnElement="Flow_Slot_AutoBook">
        <di:waypoint x="1105" y="180" />
        <di:waypoint x="1160" y="180" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_AutoBook_To_Confirm" bpmnElement="Flow_AutoBook_To_Confirm">
        <di:waypoint x="1280" y="175" />
        <di:waypoint x="1320" y="175" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Flow_Confirm_To_End" bpmnElement="Flow_Confirm_To_End">
        <di:waypoint x="1440" y="175" />
        <di:waypoint x="1482" y="175" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>
"""

LAB3_DMN = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/"
             xmlns:dmndi="https://www.omg.org/spec/DMN/20191111/DMNDI/"
             xmlns:dc="http://www.omg.org/spec/DMN/20180521/DC/"
             id="Definitions_PatientTriageRules"
             name="Hospital Patient Triage Decision Rules"
             namespace="http://camunda.org/schema/1.0/dmn"
             exporter="Camunda Modeler"
             exporterVersion="5.28.0">

  <decision id="Decision_PatientTriage" name="Educational Clinical Patient Triage Classification">
    <decisionTable id="DecisionTable_Triage" hitPolicy="FIRST">
      <input id="Input_UrgencyScore" label="Clinical Urgency Score (1-10)">
        <inputExpression id="InputExpr_UrgencyScore" typeRef="number">
          <text>urgencyScore</text>
        </inputExpression>
      </input>
      <input id="Input_SymptomsSeverity" label="Symptoms Severity Category">
        <inputExpression id="InputExpr_SymptomsSeverity" typeRef="string">
          <text>symptomsSeverity</text>
        </inputExpression>
      </input>
      <output id="Output_TriageCategory" label="Triage Classification" name="triageCategory" typeRef="string" />
      <output id="Output_TargetResponse" label="Target Response Window (Minutes)" name="targetResponseMinutes" typeRef="number" />
      <output id="Output_ClinicalProtocol" label="Clinical Protocol" name="clinicalProtocol" typeRef="string" />

      <!-- Rule 1: Urgency Score >= 8 -> Urgent Assessment -->
      <rule id="Rule_EmergencyScore">
        <inputEntry id="Entry_T1_1"><text>&gt;= 8</text></inputEntry>
        <inputEntry id="Entry_T1_2"><text>-</text></inputEntry>
        <outputEntry id="Out_T1_1"><text>"Urgent Assessment"</text></outputEntry>
        <outputEntry id="Out_T1_2"><text>15</text></outputEntry>
        <outputEntry id="Out_T1_3"><text>"Code Red: Immediate emergency human triage and resuscitation bay allocation"</text></outputEntry>
      </rule>

      <!-- Rule 2: Critical Symptoms Severity -> Urgent Assessment -->
      <rule id="Rule_CriticalSymptoms">
        <inputEntry id="Entry_T2_1"><text>-</text></inputEntry>
        <inputEntry id="Entry_T2_2"><text>"CRITICAL", "ACUTE"</text></inputEntry>
        <outputEntry id="Out_T2_1"><text>"Urgent Assessment"</text></outputEntry>
        <outputEntry id="Out_T2_2"><text>15</text></outputEntry>
        <outputEntry id="Out_T2_3"><text>"Code Red: Acute symptom profile requires direct senior clinician assessment"</text></outputEntry>
      </rule>

      <!-- Rule 3: Urgency Score 5 to 7 -> Priority Review -->
      <rule id="Rule_PriorityReview">
        <inputEntry id="Entry_T3_1"><text>[5..7]</text></inputEntry>
        <inputEntry id="Entry_T3_2"><text>-</text></inputEntry>
        <outputEntry id="Out_T3_1"><text>"Priority Review"</text></outputEntry>
        <outputEntry id="Out_T3_2"><text>240</text></outputEntry>
        <outputEntry id="Out_T3_3"><text>"Code Yellow: Priority nursing chart review and expedited slot allocation within 4h"</text></outputEntry>
      </rule>

      <!-- Rule 4: Moderate Symptoms Severity -> Priority Review -->
      <rule id="Rule_ModerateSymptoms">
        <inputEntry id="Entry_T4_1"><text>-</text></inputEntry>
        <inputEntry id="Entry_T4_2"><text>"MODERATE"</text></inputEntry>
        <outputEntry id="Out_T4_1"><text>"Priority Review"</text></outputEntry>
        <outputEntry id="Out_T4_2"><text>240</text></outputEntry>
        <outputEntry id="Out_T4_3"><text>"Code Yellow: Semi-urgent clinical condition requires same-day specialist slot"</text></outputEntry>
      </rule>

      <!-- Rule 5: Fallthrough Catch-all -> Routine -->
      <rule id="Rule_RoutineCatchall">
        <inputEntry id="Entry_T5_1"><text>-</text></inputEntry>
        <inputEntry id="Entry_T5_2"><text>-</text></inputEntry>
        <outputEntry id="Out_T5_1"><text>"Routine"</text></outputEntry>
        <outputEntry id="Out_T5_2"><text>2880</text></outputEntry>
        <outputEntry id="Out_T5_3"><text>"Code Green: Routine outpatient consultation queue within 48 hours"</text></outputEntry>
      </rule>
    </decisionTable>
  </decision>

  <dmndi:DMNDI>
    <dmndi:DMNDiagram id="DMNDiagram_Triage">
      <dmndi:DMNShape id="DMNShape_Decision_PatientTriage" dmnElementRef="Decision_PatientTriage">
        <dc:Bounds x="160" y="100" width="220" height="80" />
      </dmndi:DMNShape>
    </dmndi:DMNDiagram>
  </dmndi:DMNDI>
</definitions>
"""

# Write files to target directories
files = [
    (os.path.join(BASE_DIR, "Lab-1-Loan-Approval-Automation", "loan-approval-process.bpmn"), LAB1_BPMN),
    (os.path.join(BASE_DIR, "Lab-1-Loan-Approval-Automation", "loan-approval-rules.dmn"), LAB1_DMN),
    (os.path.join(BASE_DIR, "Lab-2-Ecommerce-Order-Fulfilment", "ecommerce-order-process.bpmn"), LAB2_BPMN),
    (os.path.join(BASE_DIR, "Lab-2-Ecommerce-Order-Fulfilment", "order-priority-rules.dmn"), LAB2_DMN),
    (os.path.join(BASE_DIR, "Lab-3-Hospital-Appointment-Triage", "hospital-appointment-process.bpmn"), LAB3_BPMN),
    (os.path.join(BASE_DIR, "Lab-3-Hospital-Appointment-Triage", "patient-triage-rules.dmn"), LAB3_DMN)
]

for path, content in files:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: {path}")

print("All BPMN and DMN models generated successfully.")
