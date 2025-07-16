import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiEndpoints } from '../utils/api';

// Custom hook for API queries
export const useApiQuery = (key, queryFn, options = {}) => {
  return useQuery(key, queryFn, {
    staleTime: 30000,
    refetchInterval: 60000,
    ...options,
  });
};

// System hooks
export const useSystemStatus = () => {
  return useApiQuery('systemStatus', apiEndpoints.systemStatus, {
    refetchInterval: 30000,
  });
};

export const useSystemMetrics = (hours = 24) => {
  return useApiQuery(['systemMetrics', hours], () => apiEndpoints.systemMetrics(hours));
};

export const useDashboardSummary = () => {
  return useApiQuery('dashboardSummary', apiEndpoints.dashboardSummary, {
    refetchInterval: 30000,
  });
};

// Stream hooks
export const useStreams = () => {
  return useApiQuery('streams', apiEndpoints.getStreams, {
    refetchInterval: 30000,
  });
};

export const useStream = (streamId) => {
  return useApiQuery(['stream', streamId], () => apiEndpoints.getStream(streamId), {
    enabled: !!streamId,
  });
};

export const useStreamAnalytics = (streamId, hours = 24) => {
  return useApiQuery(
    ['streamAnalytics', streamId, hours],
    () => apiEndpoints.getStreamAnalytics(streamId, hours),
    {
      enabled: !!streamId,
    }
  );
};

export const useStreamEvents = (streamId, eventType = null, hours = 24) => {
  return useApiQuery(
    ['streamEvents', streamId, eventType, hours],
    () => apiEndpoints.getStreamEvents(streamId, eventType, hours),
    {
      enabled: !!streamId,
    }
  );
};

// Stream mutations
export const useCreateStream = () => {
  const queryClient = useQueryClient();
  
  return useMutation(apiEndpoints.createStream, {
    onSuccess: () => {
      queryClient.invalidateQueries('streams');
      queryClient.invalidateQueries('dashboardSummary');
    },
  });
};

export const useStartStream = () => {
  const queryClient = useQueryClient();
  
  return useMutation(apiEndpoints.startStream, {
    onSuccess: () => {
      queryClient.invalidateQueries('streams');
      queryClient.invalidateQueries('systemStatus');
      queryClient.invalidateQueries('dashboardSummary');
    },
  });
};

export const useStopStream = () => {
  const queryClient = useQueryClient();
  
  return useMutation(apiEndpoints.stopStream, {
    onSuccess: () => {
      queryClient.invalidateQueries('streams');
      queryClient.invalidateQueries('systemStatus');
      queryClient.invalidateQueries('dashboardSummary');
    },
  });
};

export const useDeleteStream = () => {
  const queryClient = useQueryClient();
  
  return useMutation(apiEndpoints.deleteStream, {
    onSuccess: () => {
      queryClient.invalidateQueries('streams');
      queryClient.invalidateQueries('dashboardSummary');
    },
  });
};