import { configureStore } from "@reduxjs/toolkit";
import complaintsReducer from "./complaintsSlice.js";

export const store = configureStore({
  reducer: {
    complaints: complaintsReducer,
  },
});
