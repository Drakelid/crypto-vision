import React, { useState } from 'react';
import { Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TablePagination, TextField, InputAdornment, Skeleton } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import Page from '../components/Page';
import { useQuery } from '@tanstack/react-query';
import * as cryptoApi from '../api/crypto';
import { formatCurrency, formatPercentage } from '../utils/format';

const MarketPage: React.FC = () => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');

  const { data: cryptocurrencies, isLoading } = useQuery(
    ['cryptocurrencies'],
    () => cryptoApi.getCryptocurrencies()
  );

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const filteredCryptos = React.useMemo(() => {
    if (!cryptocurrencies) return [];
    return cryptocurrencies.filter((crypto) =>
      crypto.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      crypto.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [cryptocurrencies, searchTerm]);

  const paginatedCryptos = React.useMemo(() => {
    return filteredCryptos.slice(
      page * rowsPerPage,
      page * rowsPerPage + rowsPerPage
    );
  }, [filteredCryptos, page, rowsPerPage]);

  return (
    <Page 
      title="Market Overview"
      actions={
        <TextField
          size="small"
          placeholder="Search coins..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      }
    >
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer sx={{ maxHeight: 'calc(100vh - 250px)' }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>#</TableCell>
                <TableCell>Name</TableCell>
                <TableCell align="right">Price</TableCell>
                <TableCell align="right">24h %</TableCell>
                <TableCell align="right">Market Cap</TableCell>
                <TableCell align="right">Volume (24h)</TableCell>
                <TableCell align="right">Last 7 Days</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {isLoading ? (
                // Loading skeleton
                Array.from({ length: 5 }).map((_, index) => (
                  <TableRow key={index}>
                    <TableCell><Skeleton variant="text" width={20} /></TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Skeleton variant="circular" width={24} height={24} sx={{ mr: 1 }} />
                        <Skeleton variant="text" width={80} />
                      </Box>
                    </TableCell>
                    <TableCell align="right"><Skeleton variant="text" width={60} /></TableCell>
                    <TableCell align="right"><Skeleton variant="text" width={40} /></TableCell>
                    <TableCell align="right"><Skeleton variant="text" width={80} /></TableCell>
                    <TableCell align="right"><Skeleton variant="text" width={70} /></TableCell>
                    <TableCell align="right">
                      <Skeleton variant="rectangular" width={100} height={30} />
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                paginatedCryptos.map((crypto, index) => (
                  <TableRow hover key={crypto.id}>
                    <TableCell>{page * rowsPerPage + index + 1}</TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        {/* You can add cryptocurrency icons here */}
                        <Box sx={{ width: 24, height: 24, borderRadius: '50%', bgcolor: 'primary.main', mr: 1 }} />
                        <Box>
                          <Typography fontWeight="bold">{crypto.name}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {crypto.symbol.toUpperCase()}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Typography fontWeight="bold">
                        {formatCurrency(0)} {/* Replace with actual price data */}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography color={Math.random() > 0.5 ? 'success.main' : 'error.main'}>
                        {formatPercentage(Math.random() * 10 - 5)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(0)} {/* Replace with actual market cap data */}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(0)} {/* Replace with actual volume data */}
                    </TableCell>
                    <TableCell align="right">
                      <Box width={100} height={30}>
                        {/* Placeholder for sparkline chart */}
                        <Box
                          sx={{
                            width: '100%',
                            height: '100%',
                            bgcolor: 'action.hover',
                            borderRadius: 1,
                          }}
                        />
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredCryptos.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Page>
  );
};

export default MarketPage;
