import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { apiClient } from "../api/client.js";

// --- Thunks -----------------------------------------------------------

export const analyzeComplaintText = createAsyncThunk(
  "complaints/analyzeText",
  async (rawText, { rejectWithValue }) => {
    try {
      const { data } = await apiClient.post("/api/complaints/analyze/text", {
        raw_text: rawText,
      });
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || "Analysis failed");
    }
  }
);

export const analyzeComplaintFile = createAsyncThunk(
  "complaints/analyzeFile",
  async (file, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await apiClient.post("/api/complaints/analyze/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || "Upload analysis failed");
    }
  }
);

export const saveComplaint = createAsyncThunk(
  "complaints/save",
  async (complaintPayload, { rejectWithValue }) => {
    try {
      const { data } = await apiClient.post("/api/complaints/", complaintPayload);
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || "Save failed");
    }
  }
);

export const fetchComplaints = createAsyncThunk("complaints/fetchAll", async (_, { rejectWithValue }) => {
  try {
    const { data } = await apiClient.get("/api/complaints/");
    return data;
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || "Fetch failed");
  }
});

// --- Slice --------------------------------------------------------------

const initialState = {
  formDraft: {
    customer_name: "",
    product_name: "",
    batch_number: "",
    complaint_date: "",
    complaint_text: "",
  },
  aiAssessment: null, // full analysis response: risk, root cause, capa, duplicates, summary
  complaintsList: [],
  status: "idle", // idle | analyzing | saving | loading
  error: null,
};

const complaintsSlice = createSlice({
  name: "complaints",
  initialState,
  reducers: {
    updateFormField(state, action) {
      const { field, value } = action.payload;
      state.formDraft[field] = value;
    },
    resetForm(state) {
      state.formDraft = initialState.formDraft;
      state.aiAssessment = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // analyze (text or file) share the same result shape
      .addCase(analyzeComplaintText.pending, (state) => {
        state.status = "analyzing";
        state.error = null;
      })
      .addCase(analyzeComplaintFile.pending, (state) => {
        state.status = "analyzing";
        state.error = null;
      })
      .addCase(analyzeComplaintText.fulfilled, applyAnalysis)
      .addCase(analyzeComplaintFile.fulfilled, applyAnalysis)
      .addCase(analyzeComplaintText.rejected, applyAnalysisError)
      .addCase(analyzeComplaintFile.rejected, applyAnalysisError)

      // save
      .addCase(saveComplaint.pending, (state) => {
        state.status = "saving";
      })
      .addCase(saveComplaint.fulfilled, (state, action) => {
        state.status = "idle";
        state.complaintsList.unshift(action.payload);
        state.formDraft = initialState.formDraft;
        state.aiAssessment = null;
      })
      .addCase(saveComplaint.rejected, (state, action) => {
        state.status = "idle";
        state.error = action.payload;
      })

      // fetch list
      .addCase(fetchComplaints.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchComplaints.fulfilled, (state, action) => {
        state.status = "idle";
        state.complaintsList = action.payload;
      })
      .addCase(fetchComplaints.rejected, (state, action) => {
        state.status = "idle";
        state.error = action.payload;
      });
  },
});

function applyAnalysis(state, action) {
  state.status = "idle";
  state.aiAssessment = action.payload;
  // AI Copilot output auto-populates the Log Customer Complaint form
  state.formDraft = {
    customer_name: action.payload.customer_name || "",
    product_name: action.payload.product_name || "",
    batch_number: action.payload.batch_number || "",
    complaint_date: action.payload.complaint_date || "",
    complaint_text: action.payload.complaint_text || "",
  };
}

function applyAnalysisError(state, action) {
  state.status = "idle";
  state.error = action.payload;
}

export const { updateFormField, resetForm } = complaintsSlice.actions;
export default complaintsSlice.reducer;
